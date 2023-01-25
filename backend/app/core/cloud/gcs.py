from datetime import timedelta
from typing import Optional

from .base import BaseCloudSigner

try:
    from google import auth
    from google.auth.transport import requests
    from google.cloud.storage import Client
except ImportError as ie:
    print(
        "Please install GCS related libraries to get presigned url for gcs bucket", ie
    )


def get_presigned_gcs_url(
    bucket: str,
    blob: str,
    *,
    exp: Optional[timedelta] = None,
    content_type="application/octet-stream",
    min_size=1,
    max_size=int(1e6),
):
    """
    Compute a GCS signed upload URL without needing a private key file.
    Can only be called when a service account is used as the application
    default credentials, and when that service account has the proper IAM
    roles, like `roles/storage.objectCreator` for the bucket, and
    `roles/iam.serviceAccountTokenCreator`.
    Source: https://stackoverflow.com/a/64245028
    Parameters
    ----------
    bucket : str
        Name of the GCS bucket the signed URL will reference.
    blob : str
        Name of the GCS blob (in `bucket`) the signed URL will reference.
    exp : timedelta, optional
        Time from now when the signed url will expire.
    content_type : str, optional
        The required mime type of the data that is uploaded to the generated
        signed url.
    min_size : int, optional
        The minimum size the uploaded file can be, in bytes (inclusive).
        If the file is smaller than this, GCS will return a 400 code on upload.
    max_size : int, optional
        The maximum size the uploaded file can be, in bytes (inclusive).
        If the file is larger than this, GCS will return a 400 code on upload.
    """
    if exp is None:
        exp = timedelta(hours=1)
    credentials, project_id = auth.default()
    if credentials.token is None:
        # Perform a refresh request to populate the access token of the
        # current credentials.
        credentials.refresh(requests.Request())
    client = Client()
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(blob)
    return blob.generate_signed_url(
        version="v4",
        expiration=exp,
        service_account_email=credentials.service_account_email,
        access_token=credentials.token,
        method="PUT",
        content_type=content_type,
        headers={"X-Goog-Content-Length-Range": f"{min_size},{max_size}"},
    )


class GCSCloudSigner(BaseCloudSigner):
    def __init__(self, bucket: str, path: str, expiration: int = 3600) -> None:
        super().__init__(bucket, path, expiration)

    # TODO: pass timedelta
    def sign(self):
        signed_url = get_presigned_gcs_url(
            self.bucket, self.path, exp=timedelta(seconds=self.expiration)
        )
        return signed_url
