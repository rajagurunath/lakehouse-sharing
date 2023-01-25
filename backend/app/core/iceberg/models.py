import json
from dataclasses import dataclass, field
from typing import Dict, List

from app.core.cloud import get_presigned_url
from pyiceberg.manifest import DataFile
from pyiceberg.table import FileScanTask, Table


@dataclass
class SharingMetaData(object):
    id: str = ""
    format: Dict[str, str] = field(default_factory=dict)
    schemaString: str = ""
    partitionColumns: List[str] = field(default_factory=list)
    table: Table = None
    field_map = {
        "timestamptz": "timestamp",
        "int": "integer",
        "decimal(19, 9)": "double",
    }

    def _map_field(self, field):
        return self.field_map.get(field, field)

    def format_schema_dict(self, iceberg_dict):
        all_fields = []
        for f in iceberg_dict["fields"]:
            n = {}
            n["name"] = f.get("name")
            n["type"] = self._map_field(f.get("field_type"))
            n["nullable"] = f.get("required")
            all_fields.append(n)
        schema = {
            "type": iceberg_dict["type"],
            "fields": all_fields,
            "metadata": {
                "schema_id": iceberg_dict["schema_id"],
                "identifier_field_ids": iceberg_dict["identifier_field_ids"],
            },
        }
        return schema

    def setTable(self, table: Table):
        print("Table was set {}".format(table))
        self.table = table

    def prepare_metadata(self):
        schemaDict = self.table.metadata.schemas[0].dict()
        self.id = str(self.table.metadata.table_uuid)
        self.format = {"provider": self.table.io.properties["format"]}
        self.schemaString = json.dumps(self.format_schema_dict(schemaDict))
        self.partitionColumns = [
            field.name
            for key in self.table.specs()
            for field in self.table.specs()[key].fields
        ]

    def get_metadata(self):
        self.prepare_metadata()
        return {
            "metaData": {
                "id": self.id,
                "format": self.format,
                "schemaString": self.schemaString,
                "partitionColumns": self.partitionColumns,
            }
        }

    def get_version(self):
        self.prepare_metadata()
        return self.table.current_snapshot()

    def __repr__(self):
        return json.dumps(self.get_metadata())


@dataclass
class SharingFileStats:
    numRecords: int = 0
    minValues: Dict[str, str] = field(default_factory=dict)
    maxValues: Dict[str, str] = field(default_factory=dict)
    nullCount: Dict[str, str] = field(default_factory=dict)
    value_counts: Dict[str, str] = field(default_factory=dict)
    file: DataFile = None

    def setDataFile(self, file: DataFile):
        self.file = file

    def prepare_fie_stats(self):
        self.numRecords = self.file.dict()["record_count"]
        self.minValues = {
            k: v.decode("ISO-8859-1")
            for k, v in self.file.dict()["lower_bounds"].items()
        }
        self.maxValues = {
            k: v.decode("ISO-8859-1")
            for k, v in self.file.dict()["upper_bounds"].items()
        }
        self.nullCount = self.file.dict()["null_value_counts"]
        self.value_counts = self.file.dict()["value_counts"]

    def get_stats(self):
        self.prepare_fie_stats()
        stats = {
            "numRecords": self.numRecords,
            "minValues": self.minValues,
            "maxValues": self.maxValues,
            "nullCount": self.nullCount,
            "value_counts": self.value_counts,
        }
        return stats

    def __repr__(self):
        return json.dumps(self.get_stats())


@dataclass
class SharingFile:
    url: str = ""
    id: str = ""
    partitionValues: Dict[str, str] = field(default_factory=dict)
    size: float = 0
    file: FileScanTask = None
    stats: SharingFileStats = None

    def setFile(self, file: FileScanTask):
        self.file = file

    def prepare_file_details(self, file_expiry):
        stats = SharingFileStats()
        stats.setDataFile(self.file.file)
        stats.prepare_fie_stats()
        self.url = get_presigned_url(self.file.file.file_path, expiration=file_expiry)
        self.partitionValues = self.file.file.partition
        self.size = self.file.length
        self.stats = stats

    def get_file_details(self, file_expiry):
        self.prepare_file_details(file_expiry)
        file_details = {
            "file": {
                "url": self.url,
                "id": "123",
                "partitionValues": self.partitionValues,
                "size": self.size,
                "stats": self.stats.get_stats(),
            }
        }
        return file_details
