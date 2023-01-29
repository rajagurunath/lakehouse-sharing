import os
import sys
from abc import ABC, abstractmethod

import requests

print(sys.path)
print(os.path.abspath("."))
sys.path.insert(0, os.path.abspath("."))
from typing import Dict
from urllib.parse import urljoin

from core.api.config import Config
from core.api.jwt_auth import JWTAuth
from core.base.client import BaseClient


class RestClient(BaseClient):
    def __init__(
        self,
        baseurl: str = None,
        prefix: str = None,
        user_details: Dict[str, str] = None,
        token=None,
    ) -> None:
        self.config = Config()
        print(self.config.config)
        self.baseurl = baseurl if baseurl else self._frame_base_url()
        print(self.baseurl)
        self.prefix = prefix if prefix else self.config.get("lakehouse-sharing.prefix")
        self.token = token
        self.jauth = JWTAuth(
            self.client(),
            url=self.baseurl,
            config=self.config,
            prefix="auth",
            user_details=user_details,
        )
        super().__init__()

    def _frame_base_url(self):
        if os.environ.get("env", "local") == "local":
            host = self.config.get("lakehouse-sharing.host")
            port = self.config.get("lakehouse-sharing.port")
        else:
            host = os.environ.get("BACKEND_HOST", "0.0.0.0")
            port = os.environ.get("BACKEND_PORT", 8000)
        baseurl = f"http://{host}:{port}/"
        return baseurl

    def client(self):
        return requests

    def get_headers(self):
        if self.token is None:
            token = self.jauth.get_token()
        else:
            print("Using existing user's token")
            token = self.token
        headers = {"Authorization": f"Bearer {token}"}
        return headers

    def set_token(self, token):
        self.token = token

    def auth(self, **kwargs) -> JWTAuth:
        return self.jauth

    def form_path(self, path):
        print("form_path")
        print(self.baseurl)
        print(urljoin(self.baseurl, path))
        print("===========")
        return urljoin(self.baseurl, path)

    def post(self, path, data, **kwargs):
        url = self.form_path(path)
        print(url)
        headers = self.get_headers()
        print("headers", headers)
        res = self.client().post(url, data=data, headers=headers, **kwargs)
        return res

    def get(self, path, **kwargs):
        url = self.form_path(path)
        print(url)
        headers = self.get_headers()
        print("headers", headers)
        res = self.client().get(url, headers=headers, **kwargs)
        return res


if __name__ == "__main__":

    user_details = {"username": "admin", "password": "admin@123"}
    c = RestClient("http://localhost:8000", user_details=user_details)
    headers = c.get_headers()
    print(headers)

    list_shares = c.get("delta-sharing/shares", params={"maxResults": 2})
    print(list_shares.json())

    list_schemas = c.get(
        "delta-sharing/shares/share1/schemas", params={"maxResults": 2}
    )
    print(list_schemas.json())

    list_tables = c.get(
        "delta-sharing/shares/share1/schemas/iceberg_benchmark_db/tables",
        params={"maxResults": 2},
    )
    print(list_tables.json())

    create_share = c.post("admin/share", data={"name": "share-test##"})
    print(create_share.content)

    create_schema = c.post(
        "admin/schema",
        data={"name": "schema-test##", "table_id": 123, "share_id": "123##"},
    )
    print(create_schema.content)

    create_table = c.post(
        "admin/table",
        data={"table_name": "table-test529", "table_location": "s3://bucket/object1/"},
    )
    print(create_table.content)
