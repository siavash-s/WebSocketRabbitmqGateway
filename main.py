import os
from logging import getLogger
from queue import Queue
from autobahn.asyncio import WebSocketServerFactory
from rabbit.listener import RabbitListener
from websocket.gateway import SubscriptionGatewayServerProtocol
from utils.logging_utils import set_syslog_logging
import configs
from websocket.readers import RabbitReader
import asyncio

if __name__ == "__main__":

    # set default logging to syslog, according to ENV variable provided
    syslog_addr = os.environ.get("SYSLOG_ADDRESS", default='/dev/log')
    level = os.environ.get("LOG_LEVEL", default='INFO').upper()
    prefix = os.environ.get("LOG_PREFIX", default="WebsocketGateway")
    set_syslog_logging(syslog_addr=syslog_addr, level=level, prefix=prefix)

    # the queue between listener and reader threads
    q = Queue(-1)

    # start reader and listener threads
    reader = RabbitReader(q, SubscriptionGatewayServerProtocol.broadcast_topic)
    reader.start()
    for ws_topic, mq_configs in configs.ws_rmq_topics.items():
        for mq_conf in mq_configs:
            RabbitListener(
                mq_conf["exchange_name"],
                mq_conf["exchange_type"],
                mq_conf["topic"],
                q,
                ws_topic,
                mq_conf["hook"]
            ).start()

    factory = WebSocketServerFactory(configs.websocket_url)
    factory.protocol = SubscriptionGatewayServerProtocol
    factory.setProtocolOptions(autoPingInterval=60)
    loop = asyncio.get_event_loop()
    SubscriptionGatewayServerProtocol.loop = loop
    coro = loop.create_server(factory, configs.server_address["address"], configs.server_address["port"])
    getLogger().info(
        "listening on address: '{}' , port: {}".format(
            configs.server_address["address"], configs.server_address["port"]
        )
    )
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
    loop.close()
