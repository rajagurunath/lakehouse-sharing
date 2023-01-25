from typing import Optional, Union

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    name: str
    email: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    id: str
    encrypted_password: str


class NewUser(BaseModel):
    name: str
    password: str
    email: str
    namespace: Optional[str]
