from typing import Optional

from sqlmodel import Field, SQLModel


class Share(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    name: str = Field(unique=True)


class Table(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    table_name: str = Field(unique=True)
    table_location: str


class Schema(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    name: str = Field(unique=True)
    table_id: str = Field(default=None, foreign_key="table.id")
    share_id: str = Field(default=None, foreign_key="share.id")


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
        default=None, nullable=False, unique=True, foreign_key="user.id"
    )
    share_id: str = Field(default=None, foreign_key="share.id")
    schema_id: str = Field(default=None, foreign_key="schema.id")
    table_id: str = Field(default=None, unique=True, foreign_key="table.id")
