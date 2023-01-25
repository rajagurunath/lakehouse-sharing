from typing import Optional, Union

from pydantic import BaseModel


class ShareModel(BaseModel):
    name: str


class TableModel(BaseModel):
    table_name: str
    table_location: str


class SchemaModel(BaseModel):
    name: str
    table_id: str
    share_id: str


class PermissionModel(BaseModel):
    user_id: str
    share_id: str
    schema_name: str
    table_id: str


class TokenLifetime(BaseModel):
    username: str
    expiry: int
