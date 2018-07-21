from logging import getLogger
import requests
from requests.exceptions import ConnectionError
from configs import web_api_conf


class AuthorizeByWebApi:

    def __init__(self, token):
        self.token = token
        self.__auth_headers = {
            web_api_conf["authorization_header_key"]:
                "{} {}".format(web_api_conf["authorization_header_prefix"], token)
        }

    def authorize_identity(self) -> bool:
        try:
            response = requests.get(web_api_conf["identity_authorization_url"], headers=self.__auth_headers)
        except ConnectionError as e:
            getLogger().info("token {} cannot be authorized: cannot connect to web api: {}".format(self.token, e))
            return False
        return response.status_code == 200

    def authorize_access(self, access_type: str) -> bool:
        try:
            response = requests.get(web_api_conf["identity_authorization_url"], headers=self.__auth_headers)
        except ConnectionError as e:
            getLogger().info("token {} cannot be authorized: cannot connect to web api: {}".format(self.token, e))
            return False
        try:
            return access_type in response.json()["access"]
        except KeyError:
            getLogger().info("token {}, authorization failed. access not in web api result".format(self.token))
            return False
        except ValueError:
            getLogger().info("token {} authorization failed. web api response is not json.")
            return False
