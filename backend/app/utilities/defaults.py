import os

defaults = dict(
    SECRET_KEY="6c14d4be3699a9f66c6d3003bd62f8e14c36f08c631237cc7c88083080b9bb78",
    ALGORITHM="HS256",
    ACCESS_TOKEN_EXPIRE_MINUTES=60,
)


def get_defaults(key):
    value = os.environ.get(key, "")
    if value == "":
        value = defaults[key.upper()]
    return value
