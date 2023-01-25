from app.core.base import BaseTableFormat
from core.delta.share import DeltaFormat
from core.iceberg.share import IcebergFormat


def get_table_format_client(name):
    if name.lower() == "iceberg":
        client = IcebergFormat
    elif name.lower() == "delta":
        client = DeltaFormat
    else:
        print("No Table format available for given name {}".format(name))
    return client
