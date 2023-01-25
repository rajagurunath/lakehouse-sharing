import logging

from .base import BaseCloudSigner

try:
    import boto3
    from botocore.client import Config
    from botocore.exceptions import ClientError
except ImportError as ie:
    print("Please install AWS related libraries to get presigned url for S3 bucket", ie)


def create_presigned_s3_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client("s3", config=Config(signature_version="s3v4"))
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            HttpMethod="GET",
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


class AWSCloudSigner(BaseCloudSigner):
    def __init__(self, bucket: str, path: str, expiration: int = 3600) -> None:
        super().__init__(bucket, path, expiration)

    def sign(self):
        print(self.bucket, self.path)
        signed_url = create_presigned_s3_url(self.bucket, self.path, self.expiration)
        return signed_url
