class BaseCloudSigner(object):
    def __init__(self, bucket: str, path: str, expiration: int) -> None:
        self.bucket = bucket
        self.path = path
        self.expiration = expiration

    def sign(self):
        raise NotImplementedError
