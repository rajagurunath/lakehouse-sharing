import os
from abc import ABC, abstractmethod


class BaseClient(ABC):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    @abstractmethod
    def client(self):
        ...

    @abstractmethod
    def auth(self, **kwargs):
        ...

    @abstractmethod
    def get(self, **kwargs):
        ...

    @abstractmethod
    def post(self, **kwargs):
        ...
