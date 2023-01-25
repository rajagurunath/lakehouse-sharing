import yaml


class Config:
    def __init__(self, path="app/serverconf.yaml") -> None:
        self.path = path
        self.config = self.load_server_config()

    def load_server_config(self):
        with open(self.path, "r") as file:
            config = yaml.safe_load(file)
        return config

    def get(self, key):
        return self.config[key]
