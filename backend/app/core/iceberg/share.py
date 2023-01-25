import json

from core.base import BaseTableFormat
from core.iceberg.models import SharingFile, SharingFileStats, SharingMetaData
from pyiceberg.catalog import Catalog, load_catalog
from pyiceberg.expressions import parser
from pyiceberg.manifest import DataFile
from pyiceberg.table import FileScanTask, Table


class IcebergFormat(BaseTableFormat):
    def __init__(self) -> None:
        self.catalog = self.load_catalog()
        self.meta = SharingMetaData()
        self.file = SharingFile()
        self.table = None
        super().__init__()

    def _get_required_args(self, **kwargs):
        schema = kwargs.get("schema")
        table_name = kwargs.get("table_name")
        return schema, table_name

    def load_catalog(self) -> Catalog:
        return load_catalog("default", properties={"type": "glue"})

    def load_table(self, share, schema, table_name) -> Table:
        self.table = self.catalog.load_table("{}.{}".format(schema, table_name))

    def table_version(self, share, schema, table_name):
        self.load_table(share, schema=schema, table_name=table_name)
        # return table.metadata.table_uuid
        return str(self.table.current_snapshot().snapshot_id)

    def get_protocol(self):
        """
        dummy as of now for iceberg
        """
        protocol_json = {"protocol": {"minReaderVersion": 1}}
        return protocol_json

    def _metadata(self, share, schema, table_name):
        if self.table is None:
            self.load_table(share, schema=schema, table_name=table_name)
        self.meta.setTable(self.table)
        metadata = self.meta.get_metadata()
        return metadata

    def table_metadata(self, share, schema, table_name):
        yield json.dumps(self.get_protocol())
        yield "\n"
        yield json.dumps(self._metadata(share, schema=schema, table_name=table_name))

    def file_details(
        self,
        share,
        schema,
        table_name,
        predicateHints=None,
        limitHint=None,
        version=None,
        file_expiry=None,
    ):
        if predicateHints == "":
            parsed_filters = []
        else:
            parsed_filters = []
            for hints in predicateHints:
                parsed_filters.append(parser.parse(hints))

        yield json.dumps(self.get_protocol())
        yield "\n"
        yield json.dumps(self._metadata(share, schema=schema, table_name=table_name))
        yield "\n"

        tableScan = self.table.scan(row_filter=parsed_filters)
        sf = SharingFile()

        total_records = 0
        print(sf.stats)
        for f in tableScan.plan_files():
            sf.setFile(file=f)
            sf.prepare_file_details(file_expiry)
            print("total_records", total_records)
            yield json.dumps(sf.get_file_details(file_expiry))
            yield "\n"
            if limitHint is not None:
                total_records += sf.stats.numRecords
                if total_records >= limitHint:
                    break
