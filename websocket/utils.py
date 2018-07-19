from http.cookies import SimpleCookie
import configs


def get_token_from_cookie(raw_cookie: str) -> str:
    cookie = SimpleCookie()
    cookie.load(raw_cookie)
    try:
        token = cookie[configs.cookie_authorization["TOKEN_KEY"]].value
    except KeyError:
        return ''
    else:
        return token
