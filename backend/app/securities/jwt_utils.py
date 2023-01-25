import os
from datetime import datetime, timedelta

from app.db.auth_queries import AuthQueries
from app.models.auth import *
from app.utilities.defaults import get_defaults
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = get_defaults("SECRET_KEY")
ALGORITHM = get_defaults("ALGORITHM")
print("ACCESS_TOKEN_EXPIRE_MINUTES", os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_defaults("ACCESS_TOKEN_EXPIRE_MINUTES"))


class UserCatalog(object):
    def __init__(self) -> None:
        self.secret = self.load_secret()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.auth_db = AuthQueries()

    def load_secret(self):
        return SECRET_KEY

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def create_user(self, user: NewUser):
        userDetails = self.auth_db.check_user_exist(user.name)
        if userDetails is None:
            encrypted_password = self.get_password_hash(user.password)
            user_details = {}
            user_details["name"] = user.name
            user_details["encrypted_password"] = encrypted_password
            user_details["email"] = user.email
            user_details["namespace"] = user.namespace
            self.auth_db.create_user(user_details)
            return True
        else:
            return False

    def get_user(self, username: str):
        userDetails = self.auth_db.check_user_exist(username)
        if userDetails is not None:
            return UserInDB(**userDetails)
        else:
            return None

    def get_token_lifetime(self, user):
        token = self.auth_db.get_token_lifetime(user)
        print(token)
        return token

    def get_username_by_id(self, user_id):
        username = self.auth_db.get_username_by_id(user_id)
        return username

    def authenticate_user(self, username: str, password: str):
        print("authenticate_user", username)
        user = self.get_user(username)
        if not user:
            return False
        if not self.verify_password(password, user.encrypted_password):
            return False
        return user

    def create_access_token(
        self, data: dict, expires_delta: Union[timedelta, None] = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def list_users(self):
        users_list = self.auth_db.list_users()
        return users_list
