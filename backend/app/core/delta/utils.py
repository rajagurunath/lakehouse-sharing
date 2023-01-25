import json
import re
from typing import Any, Dict

from fsspec.core import get_fs_token_paths

PYARROW_CHECKPOINT_SCHEMA = [
    "txn",
    "add",
    "remove",
    "metaData",
    "protocol",
    "commitInfo",
]


class CustomDeltaMetaReader:
    def __init__(
        self,
        path: str,
        version: int = 0,
        checkpoint=None,
        storage_options=None,
    ):
        self.path = str(path).rstrip("/")
        self.version = version
        self.pq_files = set()
        self.delta_log_path = f"{self.path}/_delta_log"
        self.fs, self.fs_token, _ = get_fs_token_paths(
            path, storage_options=storage_options
        )
        self.checkpoint = (
            checkpoint if checkpoint is not None else self.get_checkpoint_id()
        )
        self.storage_options = storage_options
        self.schema = None

    def get_checkpoint_id(self):
        """
        if _last_checkpoint file exists, returns checkpoint_id else zero
        """
        try:
            last_checkpoint_version = json.loads(
                self.fs.cat(f"{self.delta_log_path}/_last_checkpoint")
            )["version"]
        except FileNotFoundError:
            last_checkpoint_version = 0
        return last_checkpoint_version

    def get_pq_files_from_checkpoint_parquet(self):
        """
        use checkpoint_id to get logs from parquet files
        """
        if self.checkpoint == 0:
            return
        checkpoint_path = (
            f"{self.delta_log_path}/{self.checkpoint:020}.checkpoint.parquet"
        )
        if not self.fs.exists(checkpoint_path):
            raise ValueError(
                f"Parquet file with the given checkpoint {self.checkpoint} does not exists: "
                f"File {checkpoint_path} not found"
            )
        parquet_checkpoint = self.engine.read_partition(
            fs=self.fs,
            pieces=[(checkpoint_path, None, None)],
            columns=PYARROW_CHECKPOINT_SCHEMA,
            index=None,
        )
        mm = []
        for i, row in parquet_checkpoint.iterrows():
            if row["add"] is not None or row["remove"] is not None:
                self.pq_files.add(f"{self.path}/{row['add']['path']}")
                mm.append(row)
        return mm

    def get_pq_files_from_delta_json_logs(self):
        """
        start from checkpoint id, collect logs from every json file until the
        given version
        example:
            checkpoint 10, version 16
                1. read the logs from 10th checkpoint parquet ( using above func)
                2. read logs from json files until version 16
        log Collection:
            for reading the particular version of delta table, We are concerned
            about `add` and `remove` Operation (transaction) only.(which involves
            adding and removing respective parquet file transaction)
        """
        log_files = self.fs.glob(
            f"{self.delta_log_path}/{self.checkpoint // 10:019}*.json"
        )
        if len(log_files) == 0:
            raise RuntimeError(
                f"No Json files found at _delta_log_path:- {self.delta_log_path}"
            )
        log_files = sorted(log_files)
        log_versions = [
            int(re.findall(r"(\d{20})", log_file_name)[0])
            for log_file_name in log_files
        ]
        if (self.version is not None) and (self.version not in log_versions):
            raise ValueError(
                f"Cannot time travel Delta table to version {self.version}, Available versions for given "
                f"checkpoint {self.checkpoint} are {log_versions}"
            )
        mm = []
        for log_file_name, log_version in zip(log_files, log_versions):
            print(log_file_name)
            log = self.fs.cat(log_file_name).decode().split("\n")
            for line in log:
                if line:  # for last empty line
                    meta_data = json.loads(line)

                    if "add" in meta_data.keys():
                        file = f"{self.path}/{meta_data['add']['path']}"
                        meta_data["add"]["path"] = file
                        mm.append(meta_data)
                    elif "remove" in meta_data.keys():
                        remove_file = f"{self.path}/{meta_data['remove']['path']}"
                        meta_data["remove"]["path"] = remove_file
            if self.version == int(log_version):
                break
        return mm

    def get_metafiles(self) -> Dict[str, Any]:
        files1 = self.get_pq_files_from_checkpoint_parquet()
        files2 = self.get_pq_files_from_delta_json_logs()
        files = []
        if files1 is None:
            files = files2
        else:
            files += files1
            files += files2
        return files
