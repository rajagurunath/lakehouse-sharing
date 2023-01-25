from pydantic import BaseModel, Field

from .common import Schema, Share


class GetShareResponse(BaseModel):
    share: Share


class SchemaResponse(BaseModel):
    name: str
    share: str


class TableResponse(BaseModel):
    name: str
    schemaName: str = Field(alias="schema")
    share: str
    shareId: str
    id: str


class CommonErrorResponse(BaseModel):
    errorCode: str
    message: str
