from autobahn.asyncio import WebSocketServerProtocol
from autobahn.websocket import ConnectionDeny
from authorization.web_api_authorization import AuthorizeByWebApi
from messages.messages import errors
from websocket.utils import get_token_from_cookie


class SubscriptionGatewayServerProtocol(WebSocketServerProtocol):
    loop = None
    subscription_connections = {}
    authorization_class = AuthorizeByWebApi

    def onConnect(self, request):
        try:
            raw_cookie = request.headers['cookie']
        except KeyError:
            raise ConnectionDeny(400, errors.get("NO_COOKIE", ''))
        else:
            token = get_token_from_cookie(raw_cookie)
            if not token:
                raise ConnectionDeny(400, errors.get("TOKEN_COOKIE_PARSE", ""))
            if not self.authorization_class(token).authorize_identity():
                raise ConnectionDeny(401, errors.get("INVALID_TOKEN", ""))
