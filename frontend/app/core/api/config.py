import os

import yaml
from toolz.dicttoolz import get_in


class Config:
    def __init__(self, path="config.yaml") -> None:
        print(os.getcwd())
        self.path = path
        self.config = self.load_server_config()

    def load_server_config(self):
        with open(self.path, "r") as file:
            config = yaml.safe_load(file)
        return config

    def get(self, key):
        keys = key.split(".")
        return get_in(keys, self.config)
