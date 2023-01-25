import os
from abc import ABC, abstractmethod
from typing import Dict
from urllib.parse import urljoin

from app.core.api.config import Config
from core.base.auth import BaseAuth
from requests import Request

URL = os.environ.get("delta-sharing-url", "http://localhost:8000")


class JWTAuth(BaseAuth):
    def __init__(
        self, client: Request, url, config: Config, prefix="auth", user_details=None
    ) -> None:
        self.client = client
        self.url = url
        self.prefix = prefix
        self.config = config
        if user_details is None:
            self.load_user_details()
        else:
            self.user_details = user_details
        super().__init__(url=url)

    def load_user_details(self):
        self.user_details = {
            "username": self.config.get("lakehouse-sharing.username"),
            "password": self.config.get("lakehouse-sharing.password"),
        }

    def path_join(self, *args):
        url = "{base}{}".format("/".join(args), base=self.url)
        return url

    def get_token(self, path="token"):
        url = self.path_join(self.prefix, path)
        print("get_token", url, self.user_details)
        response = self.client.post(url, headers={}, data=self.user_details)
        print(response.content)
        if response.status_code != 200:
            raise Exception(response.content)
        token = response.json()["access_token"]
        return token


if __name__ == "__main__":
    jauth = JWTAuth()
    jauth.get_headers({"username": "admin", "password": "admin@123"})
