import json

from app.db.queries import Query
from core.base import BaseTableFormat
from core.delta.models import SharingFile, SharingFileStats, SharingMetaData
from core.delta.utils import CustomDeltaMetaReader
from deltalake.data_catalog import DataCatalog
from deltalake.table import DeltaTable


class DeltaFormat(BaseTableFormat):
    def __init__(self) -> None:
        self.catalog = self.load_catalog()
        self.meta = SharingMetaData()
        self.file = SharingFile()
        self.table: DeltaTable = None
        self.meta_db = Query()
        self.path = None
        self.__post_init__()
        super().__init__()

    def __post_init__(self):
        """To pass creds to deltalake underlying rust lib"""
        import os

        from boto3.session import Session

        session = Session()
        credentials = session.get_credentials()
        if credentials is not None:
            current_credentials = credentials.get_frozen_credentials()
            os.environ["AWS_ACCESS_KEY_ID"] = current_credentials.access_key
            os.environ["AWS_SECRET_ACCESS_KEY"] = current_credentials.secret_key

    def load_catalog(self) -> DataCatalog:
        return DataCatalog.AWS

    def get_path(self, share: str, schema: str, table_name: str):
        self.path = self.meta_db.get_path(share=share, schema=schema, table=table_name)
        if self.path is None:
            raise ValueError(f"Table {table_name} doesn't exist")

    def load_table(self, share: str, schema: str, table_name: str):
        self.get_path(share=share, schema=schema, table_name=table_name)
        self.table = DeltaTable(self.path)

    def table_version(self, share: str, schema: str, table_name: str):
        self.get_path(share=share, schema=schema, table_name=table_name)
        self.load_table(share=share, schema=schema, table_name=table_name)
        # return table.metadata.table_uuid
        return str(self.table.version())

    def get_protocol(self):
        """
        dummy as of now for iceberg
        """
        protocol_json = {
            "protocol": {
                "minReaderVersion": self.table.protocol().min_reader_version,
                "minWriterVersion": self.table.protocol().min_writer_version,
            }
        }
        return protocol_json

    def _metadata(self, share: str, schema: str, table_name: str):
        self.get_path(share=share, schema=schema, table_name=table_name)
        if self.table is None:
            self.load_table(self.path)
        self.meta.setTable(self.table)
        metadata = self.meta.get_metadata()
        return metadata

    def table_metadata(self, share: str, schema: str, table_name: str):
        yield json.dumps(self.get_protocol())
        yield "\n"
        yield json.dumps(
            self._metadata(share=share, schema=schema, table_name=table_name)
        )

    def file_details(
        self,
        share: str,
        schema: str,
        table_name: str,
        predicateHints=None,
        limitHint=None,
        version=None,
        file_expiry=3600,
    ):
        if predicateHints == "":
            predicateHints = []
        self.get_path(share=share, schema=schema, table_name=table_name)
        yield json.dumps(self.get_protocol())
        yield "\n"
        yield json.dumps(
            self._metadata(share=share, schema=schema, table_name=table_name)
        )
        yield "\n"
        cdr = CustomDeltaMetaReader(path=self.path, version=version)
        files = cdr.get_metafiles()
        sf = SharingFile()

        total_records = 0
        print(sf.stats)
        for f in files:
            sf.setFile(file=f)
            sf.prepare_file_details(file_expiry)
            print("total_records", total_records)
            yield json.dumps(sf.get_file_details(file_expiry))
            yield "\n"
            if limitHint is not None:
                total_records += sf.stats.numRecords
                if total_records >= limitHint:
                    break
