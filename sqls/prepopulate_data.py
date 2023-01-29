import os
import uuid
from typing import Optional

from passlib.context import CryptContext
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Share(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    name: str = Field(unique=True)
    created_by: str = Field(default=None, nullable=False, foreign_key="user.id")


class Table(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}
    id: str = Field(primary_key=True)
    table_name: str = Field(unique=True)
    table_location: str
    created_by: str = Field(default=None, nullable=False, foreign_key="user.id")


class Schema(SQLModel, table=True):
    # __table_args__ = {"extend_existing": True}

    id: str = Field(primary_key=True)
    name: str = Field(unique=True)
    table_id: str = Field(default=None, foreign_key="table.id")
    share_id: str = Field(default=None, foreign_key="share.id")
    created_by: str = Field(default=None, nullable=False, foreign_key="user.id")


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
    user_id: str = Field(default=None, nullable=False, foreign_key="user.id")
    share_id: str = Field(default=None, foreign_key="share.id")
    schema_id: str = Field(default=None, foreign_key="schema.id")
    table_id: str = Field(default=None, foreign_key="table.id")


def create_db_connection():
    if os.environ.get("env", "local") == "local":
        # for manual setup
        sqlite_url = os.environ.get("db_url")
        print("local", sqlite_url)
        engine = create_engine(
            sqlite_url,
            echo=True,
        )
        # SQLModel.metadata.create_all(engine, checkfirst=True)
        return engine
    else:
        # for docker setup
        pg_url = "postgresql+psycopg2://root:password@localhost:5433/postgres"
        engine = create_engine(pg_url, echo=True)
        SQLModel.metadata.create_all(engine)
        return engine


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
get_hashed_passw = lambda password: pwd_context.hash(password)
get_user_id = lambda: uuid.uuid4().hex
password = get_hashed_passw("admin@123")

engine = create_db_connection()
session = Session(engine)
SQLModel.metadata.create_all(engine)
session.commit()

user5 = User(
    id=get_user_id(),
    name="admin",
    email="admin@lakehouse.com",
    team="open-source",
    encrypted_password=password,
    namespace="data-team",
)

session.add(user5)
session.commit()

delta_share1 = Share(name="delta_share1", id=str(uuid.uuid4()), created_by=user5.id)
iceberg_share = Share(name="iceberg_share", id=str(uuid.uuid4()), created_by=user5.id)
delta_share2 = Share(name="delta_share2", id=str(uuid.uuid4()), created_by=user5.id)
delta_share3 = Share(name="delta_share3", id=str(uuid.uuid4()), created_by=user5.id)


delta_table1 = Table(
    table_name="test_hm",
    id=str(uuid.uuid4()),
    table_location="s3://tf-benchmarking/delta_2/dwh/test_hm",
    created_by=user5.id,
)
delta_table2 = Table(
    table_name="test_student",
    id=str(uuid.uuid4()),
    table_location="s3://tf-benchmarking/delta_2/dwh/test_student",
    created_by=user5.id,
)

delta_table3 = Table(
    table_name="test_teacher",
    id=str(uuid.uuid4()),
    table_location="s3://tf-benchmarking/delta_2/dwh/test_teacher",
    created_by=user5.id,
)

iceberg_table4 = Table(
    table_name="iceberg_benchmark_nyc_taxi_trips_v2",
    id=str(uuid.uuid4()),
    table_location="s3://dummy-bucket/iceberg_benchmark_nyc_taxi_trips_v2",
    created_by=user5.id,
)

schema1tb1 = Schema(
    name="delta_schema",
    share_id=delta_share1.id,
    id=str(uuid.uuid4()),
    table_id=delta_table1.id,
    created_by=user5.id,
)

schema1tb2 = Schema(
    name="delta_schema1",
    share_id=delta_share1.id,
    id=str(uuid.uuid4()),
    table_id=delta_table2.id,
    created_by=user5.id,
)


schema2tb1 = Schema(
    name="schema2",
    share_id=delta_share2.id,
    id=str(uuid.uuid4()),
    table_id=delta_table1.id,
    created_by=user5.id,
)

schema2tb2 = Schema(
    name="schema2",
    share_id=delta_share2.id,
    id=str(uuid.uuid4()),
    table_id=delta_table2.id,
    created_by=user5.id,
)

schema3tb3 = Schema(
    name="delta_schema2",
    share_id=delta_share3.id,
    id=str(uuid.uuid4()),
    table_id=delta_table3.id,
    created_by=user5.id,
)

schema4tb3 = Schema(
    name="tripsdb",
    share_id=iceberg_share.id,
    id=str(uuid.uuid4()),
    table_id=iceberg_table4.id,
    created_by=user5.id,
)


permission1 = Permission(
    id=str(uuid.uuid4()),
    user_id=user5.id,
    share_id=schema1tb1.share_id,
    schema_id=schema1tb1.id,
    table_id=schema1tb1.table_id,
)
permission2 = Permission(
    id=str(uuid.uuid4()),
    user_id=user5.id,
    schema_id=schema2tb1.id,
    share_id=schema2tb1.share_id,
    table_id=schema2tb1.table_id,
)
permission3 = Permission(
    id=str(uuid.uuid4()),
    user_id=user5.id,
    schema_id=schema2tb1.id,
    share_id=schema2tb1.share_id,
    table_id=schema2tb1.table_id,
)
permission4 = Permission(
    id=str(uuid.uuid4()),
    user_id=user5.id,
    schema_id=schema3tb3.id,
    share_id=schema3tb3.share_id,
    table_id=schema3tb3.table_id,
)
permission5 = Permission(
    id=str(uuid.uuid4()),
    user_id=user5.id,
    schema_id=schema4tb3.id,
    share_id=schema4tb3.share_id,
    table_id=schema4tb3.table_id,
)

tlf = TokenLifetime(id=str(uuid.uuid4()), user_id=user5.id, expiry="604800")

session.add(delta_share1)
session.add(delta_share2)
session.add(delta_share3)
session.add(iceberg_share)
session.commit()

session.add(delta_table1)
session.add(delta_table2)
session.add(delta_table3)
session.add(iceberg_table4)
session.commit()

session.add(schema1tb1)
session.add(schema1tb2)

session.add(schema2tb1)
# session.add(schema2tb2)

session.add(schema3tb3)
session.add(schema4tb3)
session.commit()


session.add(tlf)

session.add(permission1)
session.add(permission2)
session.add(permission3)
session.add(permission4)
session.add(permission5)
session.commit()
