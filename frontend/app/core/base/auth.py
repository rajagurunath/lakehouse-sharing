import os
from abc import ABC, abstractmethod

import requests


class BaseAuth(ABC):
    def __init__(self, url) -> None:
        self.url = url
        self.prefix = "auth"
        super().__init__()

    def get_headers(self):
        ...

    def get_token(self, path):
        ...
