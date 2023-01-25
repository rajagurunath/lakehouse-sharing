import json
from dataclasses import dataclass, field
from typing import Any, Dict, List

from app.core.cloud import get_presigned_url
from deltalake import DeltaTable


@dataclass
class SharingMetaData(object):
    id: str = ""
    format: Dict[str, str] = field(default_factory=dict)
    schemaString: str = ""
    partitionColumns: List[str] = field(default_factory=list)
    table: DeltaTable = None

    def setTable(self, table: DeltaTable):
        print("Table was set {}".format(table))
        self.table = table

    def prepare_metadata(self):
        schemaDict = self.table.schema().to_json()
        self.id = str(self.table.metadata().id)
        self.format = {"provider": "parquet"}
        self.schemaString = schemaDict
        self.partitionColumns = self.table.metadata().partition_columns

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
        return self.table.version()

    def __repr__(self):
        return json.dumps(self.get_metadata())


@dataclass
class SharingFileStats:
    numRecords: int = 0
    minValues: Dict[str, str] = field(default_factory=dict)
    maxValues: Dict[str, str] = field(default_factory=dict)
    nullCount: Dict[str, str] = field(default_factory=dict)
    file: Dict[str, Any] = None

    def setDataFile(self, file: Dict[str, Any]):
        self.file = file

    def prepare_fie_stats(self):
        self.numRecords = self.file["numRecords"]
        self.minValues = self.file["minValues"]
        self.maxValues = self.file["maxValues"]
        self.nullCount = self.file["nullCount"]

    def get_stats(self):
        self.prepare_fie_stats()
        stats = {
            "numRecords": self.numRecords,
            "minValues": self.minValues,
            "maxValues": self.maxValues,
            "nullCount": self.nullCount,
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
    file: Dict[str, Any] = None
    stats: SharingFileStats = None

    def setFile(self, file: Dict[str, Any]):
        self.file = file

    def prepare_file_details(self, file_expiry: int):
        stats = SharingFileStats()
        # key will be `add`` or `remove`
        key = list(self.file.keys())[0]
        stats.setDataFile(json.loads(self.file[key]["stats"]))
        stats.prepare_fie_stats()
        self.url = get_presigned_url(self.file[key]["path"], expiration=file_expiry)
        self.partitionValues = self.file[key]["partitionValues"]
        self.size = self.file[key]["size"]
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
