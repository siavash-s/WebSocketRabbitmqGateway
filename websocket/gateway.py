from json import JSONDecodeError
from logging import getLogger
from autobahn.asyncio import WebSocketServerProtocol
from marshmallow import ValidationError
from authorization.web_api_authorization import AuthorizeByWebApi
from configs import ws_rmq_topics
from schema.schema import SubscriptionRequest, SubscriptionResponse, PublishPayload


class SubscriptionGatewayServerProtocol(WebSocketServerProtocol):
    loop = None
    subscription_connections = {k: set() for k in ws_rmq_topics}
    authorization_class = AuthorizeByWebApi

    def onConnect(self, request):
        getLogger().info("Client '{}' connected".format(self.peer))

    def onMessage(self, payload, isBinary):
        if not isBinary:
            str_payload = payload.decode('utf8')
            in_schema = SubscriptionRequest()
            out_schema = SubscriptionResponse()
            try:
                input_data = in_schema.loads(str_payload)
            except ValidationError as e:
                getLogger().info(
                    "invalid data from client '{}', data:'{}' error: '{}'".format(self.peer, str_payload, e)
                )
                self.sendMessage(
                    out_schema.dumps({
                        'result': False,
                        'detail': "bad format fields: {}".format(e.field_names)
                    }).encode("utf8"),
                    isBinary=False
                )
                return
            except JSONDecodeError as e:
                getLogger().info(
                    "json from client '{}' cannot be decoded,data: '{}', error: '{}'".format(self.peer, str_payload, e)
                )
                self.sendMessage(
                    out_schema.dumps({
                        'result': False,
                        'detail': "bad json format"
                    }).encode("utf8"),
                )
            else:
                if not self.authorization_class(input_data["token"]).authorize_access('r'):
                    self.sendMessage(
                        out_schema.dumps({
                            'result': False,
                            'detail': "token access denied"
                        }).encode("utf8"),
                        isBinary=False
                    )
                    return
                if input_data["topic"] not in self.subscription_connections:
                    getLogger().info(
                        "client token '{}' cannot subscribe '{}', topic does not exists".format(
                            input_data["token"],
                            input_data["topic"],
                        )
                    )
                    self.sendMessage(
                        out_schema.dumps({
                            'result': False,
                            'detail': "topic does not exist"
                        }).encode("utf8"),
                        isBinary=False
                    )
                    return
                # everything is ok
                else:
                    self.subscription_connections[input_data["topic"]].add(self)
                    getLogger().info(
                        "client subscribed on '{}' with token '{}'".format(input_data["topic"], input_data["token"])
                    )
                    self.sendMessage(
                        out_schema.dumps({
                            'result': True
                        }).encode("utf8"),
                        isBinary=False
                    )

    def onClose(self, wasClean, code, reason):
        getLogger().info(
            "client '{}' closed the connection, reason: {}".format(self.peer, reason)
        )
        for connections_sets in list(self.subscription_connections.values()):
            if self in connections_sets:
                connections_sets.remove(self)

    @classmethod
    def broadcast_topic(cls, topic: str, msg: str):
        """broadcast the provided message to the specified topic.

        :param msg: the message to send.
        :param topic: the topic in which the message should broadcast.
        :raises KeyError: if the topic does not exists.
        """
        try:
            connections = cls.subscription_connections[topic]
        except KeyError as e:
            getLogger("topic {} does not exists".format(topic))
            raise e
        out_schema = PublishPayload()
        for connection in connections:
            cls.loop.call_soon_threadsafe(
                cls.sendMessage,
                connection,
                out_schema.dumps({"topic": topic, "payload": msg}).encode('utf8'),
            )
