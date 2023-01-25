from typing import Dict

from app.db.tables import TokenLifetime, User
from app.utilities import get_random_uuid_hex
from db.queries import create_db_connection
from sqlmodel import Session, select


class AuthQueries:
    def __init__(self) -> None:
        self.engine = create_db_connection()

    def execute_sql(self, stmt):
        with Session(self.engine) as session:
            results = session.exec(statement=stmt).all()
            print(results)
        return results

    def check_user_exist(self, name):
        stmt = select(User).where(User.name == name)
        print(stmt)
        rows = self.execute_sql(stmt)
        print(rows)
        if len(rows) > 0:
            res = {
                "name": rows[0].name,
                "id": rows[0].id,
                "email": rows[0].email,
                "encrypted_password": rows[0].encrypted_password,
            }
        else:
            res = None
        return res

    def create_user(self, user_details: Dict):
        user = User(
            id=get_random_uuid_hex(),
            name=user_details["name"],
            email=user_details["email"],
            encrypted_password=user_details["encrypted_password"],
            namespace=user_details.get("namespace", "EDP"),
        )
        session = Session(self.engine)
        session.add(user)
        session.commit()
        return True

    def get_token_lifetime(self, user):
        stmt = (
            select(User, TokenLifetime)
            .where(User.id == TokenLifetime.user_id)
            .where(User.id == user)
        )
        rows = self.execute_sql(stmt)
        if rows:
            user, token = rows[0]
            return int(token.expiry)

    def list_users(self):
        stmt = select(User.name, User.id)
        rows = self.execute_sql(stmt)
        return rows

    def get_username_by_id(self, user_id):
        stmt = select(User.name).where(User.id == user_id)
        rows = self.execute_sql(stmt)
        if rows:
            return rows[0]
