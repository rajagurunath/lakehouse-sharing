from typing import List, Optional

from pydantic import BaseModel


class Share(BaseModel):
    id: Optional[str]
    name: str


class Schema(BaseModel):
    name: str
    share: str


class QueryModel(BaseModel):
    predicateHints: Optional[List[str]] = ""
    limitHint: Optional[int]
    version: Optional[int]
