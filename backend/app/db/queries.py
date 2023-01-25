import os

from app.conf import Config
from app.db.tables import Permission, Schema, Share, Table, TokenLifetime, User
from app.utilities import get_random_uuid

# from .utils import create_db_connection
from sqlmodel import Session, SQLModel, create_engine, select

conf = Config()


def create_db_connection():
    if os.environ.get("env", "local") == "local":

        sqlite_url = os.environ.get("db_url")
        print("local", sqlite_url)
        engine = create_engine(
            sqlite_url,
            echo=True,
        )
        # SQLModel.metadata.create_all(engine, checkfirst=True)
        return engine
    else:
        db_conf = conf.get("db")
        POSTGRES_USER = os.environ.get("POSTGRES_USER")
        POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
        POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
        POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
        POSTGRES_DB = os.environ.get("POSTGRES_DB")
        postgres_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
        engine = create_engine(
            postgres_url,
            echo=True,
        )
        return engine


def create_db_and_tables():
    engine = create_db_connection()
    session = Session(engine)
    SQLModel.metadata.create_all(engine)
    session.commit()


class Query:
    def __init__(self, engine=None) -> None:
        if engine is None:
            self.engine = create_db_connection()
        else:
            self.engine = engine

    def execute_sql(self, stmt):
        with Session(self.engine) as session:
            results = session.exec(statement=stmt).all()
            print(results)
        return results

    def list_shares(self, user_id):
        stmt = (
            select(Share)
            .select_from(Permission)
            .where(Share.id == Permission.share_id)
            .where(Permission.user_id == user_id)
            .distinct(Share.name)
        )
        print("list_shares sql", stmt.compile())
        results = self.execute_sql(stmt)
        return results

    def get_share(self, share, user_id):
        stmt = (
            select(Share)
            .select_from(Permission)
            .where(Share.id == Permission.share_id)
            .where(Permission.user_id == user_id)
            .where(Share.name == share)
        )
        rows = self.execute_sql(stmt)
        if len(rows) > 0:
            res = {"id": rows[0].id, "name": rows[0].name}
        else:
            res = None
        return res

    def list_schemas(self, share):
        stmt = select(Share, Schema).join(Schema).where(Share.name == share)
        rows = self.execute_sql(stmt)
        res = [{"name": schema.name, "share": share.name} for (share, schema) in rows]
        return res

    def list_tables(self, share, schema):
        stmt = (
            select(Share, Schema, Table)
            .where(Share.id == Schema.share_id, Schema.table_id == Table.id)
            .where(Share.name == share, Schema.name == schema)
        )
        rows = self.execute_sql(stmt)
        res = [
            {
                "name": table.table_name,
                "schema": schema.name,
                "share": share.name,
                "shareId": share.id,
                "id": table.id,
            }
            for (share, schema, table) in rows
        ]
        return res

    def check_user_permission(self, user_id, share, schema=None, table=None):
        with Session(self.engine) as session:
            statement = (
                session.query(Permission)
                .select_from(Permission)
                .join(Share)
                .join(Schema)
                .join(Table)
                .where(Permission.user_id == user_id)
            )
            if share:
                statement = statement.where(Share.name == share)
            if schema:
                statement = statement.where(Schema.name == schema)
            if table:
                statement = statement.where(Table.table_name == table)
            statement = statement.with_entities(
                Share.name, Table.table_name, Schema.name
            )
            # statement = select(Permission, Share.name,).join(Share).join(Schema).join(Table)
            # stmt = perm.query.join(Share)
            results = session.exec(statement).all()
        return True if results else False

    def list_all_tables(self, share, user_id):
        stmt = (
            select(Share, Schema, Table)
            .select_from(Permission)
            .where(Share.id == Permission.share_id)
            .where(Permission.user_id == user_id)
            .where(Share.id == Schema.share_id, Schema.table_id == Table.id)
            .where(Share.name == share)
        )
        rows = self.execute_sql(stmt)
        res = [
            {
                "name": table.table_name,
                "schema": schema.name,
                "share": share.name,
                "shareId": share.id,
                "id": table.id,
            }
            for (share, schema, table) in rows
        ]
        return res

    def check_schema_and_table_existance(self, share, schema=None, table=None):

        if (share is not None) and (schema is None) and (table is None):
            stmt = select(Share).where(Share.name == share)
        if (share is not None) and (schema is not None) and (table is None):
            stmt = (
                select(Share, Schema)
                .where(Share.id == Schema.share_id, Schema.table_id == Table.id)
                .where(Schema.name == schema)
            )
        if (share is not None) and (schema is not None) and (table is not None):
            stmt = (
                select(Share, Schema, Table)
                .where(Share.id == Schema.share_id, Schema.table_id == Table.id)
                .where(Table.table_name == table)
            )
        sql = stmt.compile()
        print("compiled sql", sql)
        rows = self.execute_sql(stmt)
        return True if len(rows) != 0 else False

    def get_path(self, share, schema, table):
        stmt = (
            select(Share, Schema, Table)
            .where(Share.id == Schema.share_id, Schema.table_id == Table.id)
            .where(Share.name == share)
            .where(Schema.name == schema)
            .where(Table.table_name == table)
        )
        rows = self.execute_sql(stmt)
        if len(rows) > 0:
            _, _, table = rows[0]
            return table.table_location


class AdminQuery:
    def __init__(self) -> None:
        self.engine = create_db_connection()

    def get_session(self):
        session = Session(self.engine)
        return session

    # def add(self,model:SQLModel):
    #     with Session(self.engine) as session:
    #         session.add(model)
    def add(self, model: SQLModel):
        session = Session(self.engine)
        session.add(model)
        session.commit()
        session.close()

    def execute_sql(self, stmt):
        with Session(self.engine) as session:
            results = session.exec(statement=stmt).all()
            print(results)
        return results

    def create_share(self, share: Share):
        shareTable = Share(id=get_random_uuid(), name=share.name)
        self.add(shareTable)

    def create_schema(self, schema: Schema):
        schemaTable = Schema(
            id=get_random_uuid(),
            name=schema.name,
            table_id=schema.table_id,
            share_id=schema.share_id,
        )
        self.add(schemaTable)

    def create_table(self, table: Table):
        tableTable = Table(
            id=get_random_uuid(),
            table_name=table.table_name,
            table_location=table.table_location,
        )
        self.add(tableTable)

    def get_schema_id_by_name(self, share_id, schemaname):
        stmt = select(Schema.id).where(
            Schema.share_id == share_id, Schema.name == schemaname
        )
        rows = self.execute_sql(stmt=stmt)
        return rows

    def link_resources(self, resources: Permission):
        schema_id = self.get_schema_id_by_name(
            resources.share_id, resources.schema_name
        )[0]
        perm = Permission(
            id=get_random_uuid(),
            user_id=resources.user_id,
            share_id=resources.share_id,
            schema_id=schema_id,
            table_id=resources.table_id,
        )
        self.add(perm)

    def get_id_by_user(self, user_name):
        stmt = select(User.id).where(User.name == user_name)
        rows = self.execute_sql(stmt)
        return rows[0]

    def add_lifetime(self, user_id, expiry):
        lifetime = TokenLifetime(id=get_random_uuid(), user_id=user_id, expiry=expiry)
        self.add(lifetime)
