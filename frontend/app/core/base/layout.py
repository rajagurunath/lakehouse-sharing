import os
from abc import ABC, abstractmethod

import requests
from core.base.client import BaseClient


class BaseLayout(ABC):
    client: BaseClient

    def __init__(self) -> None:
        self.layouts = {}

    @abstractmethod
    def get_layout(self):
        raise NotImplementedError
