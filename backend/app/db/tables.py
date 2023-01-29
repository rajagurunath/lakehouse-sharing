from typing import Optional

from sqlmodel import Field, SQLModel


class Share(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    name: str = Field(unique=True) 
    created_by:str = Field(
        default=None, nullable=False, foreign_key="user.id"
    )


class Table(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    table_name: str = Field(unique=True)
    table_location: str
    created_by:str = Field(
        default=None, nullable=False, foreign_key="user.id"
    )


class Schema(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    name: str = Field(unique=True)
    table_id: str = Field(default=None, foreign_key="table.id")
    share_id: str = Field(default=None, foreign_key="share.id")
    created_by:str = Field(
        default=None, nullable=False, foreign_key="user.id"
    )


class User(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    name: str = Field(unique=True)
    email: str
    encrypted_password: str
    namespace: str


class TokenLifetime(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    user_id: str = Field(default=None, unique=True, foreign_key="user.id")
    expiry: int


class Permission(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    user_id: str = Field(
        default=None, nullable=False, foreign_key="user.id"
    )
    share_id: str = Field(default=None, foreign_key="share.id")
    schema_id: str = Field(default=None, foreign_key="schema.id")
    table_id: str = Field(default=None, foreign_key="table.id")
