from urllib.parse import urlparse

from .aws import AWSCloudSigner
from .azure import AzureCloudSigner
from .gcs import GCSCloudSigner


def get_presigned_url(s3_path, expiration=3600):
    path = urlparse(s3_path)
    bucket = path.netloc
    objpath = path.path.lstrip("/")
    if path.scheme == "s3" or path.scheme == "s3a":
        s3 = AWSCloudSigner(bucket=bucket, path=objpath, expiration=expiration)
        signed_url = s3.sign()
    elif path.scheme == "gs":
        gcs = GCSCloudSigner(bucket=bucket, path=objpath, expiration=expiration)
        signed_url = gcs.sign()
    elif path.scheme == "adfs":
        adfs = AzureCloudSigner(bucket=bucket, path=path, expiration=expiration)
        signed_url = adfs.sign()
    return signed_url
