from datetime import datetime, timedelta

from .base import BaseCloudSigner

try:
    from azure.storage.blob import BlobSasPermissions, generate_blob_sas
except ImportError as ie:
    print(
        "Please install Azure related libraries to get presigned url for Azure container ",
        ie,
    )


def generate_download_signed_url(
    azure_account_name, azure_container, azure_blob, expiration, azure_primary_key
):
    sas_blob = generate_blob_sas(
        account_name=azure_account_name,
        container_name=azure_container,
        blob_name=azure_blob,
        account_key=azure_primary_key,
        # For writing back to the Azure Blob set write and create to True
        permission=BlobSasPermissions(read=True, write=False, create=False),
        # This URL will be valid for 1 hour
        expiry=datetime.utcnow() + timedelta(hours=1),
    )
    url = (
        "https://"
        + azure_account_name
        + ".blob.core.windows.net/"
        + azure_container
        + "/"
        + azure_blob
        + "?"
        + sas_blob
    )

    print("Generated GET signed URL:")
    print(url)
    print("You can use this URL with any user agent, for example:")
    print("curl '{}'".format(url))
    return url


class AzureCloudSigner(BaseCloudSigner):
    def __init__(self, bucket: str, path: str, expiration: int = 3600) -> None:
        self.azure_account_name = ""
        self.azure_primary_key = ""
        super().__init__(bucket, path, expiration)

    def sign(self):
        signed_url = generate_download_signed_url(
            azure_account_name=self.azure_account_name,
            azure_container=self.bucket,
            azure_blob=self.path,
            expiration=self.expiration,
            azure_primary_key=self.azure_primary_key,
        )
        return signed_url
