from datetime import datetime, timedelta
from typing import Union

from app.db.auth_queries import AuthQueries
from app.models.auth import *
from app.securities.user_auth import *
from app.utilities.exceptions import LakehouseShareException
from fastapi import Depends, FastAPI, status
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise LakehouseShareException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="Unauthorized User",
        )
    # token_lifetime = auth.get_token_lifetime(user)
    token_expiry = ACCESS_TOKEN_EXPIRE_MINUTES
    access_token_expires = timedelta(minutes=token_expiry)
    access_token = auth.create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/add_user")
async def create_user(
    user: NewUser, current_user: User = Depends(get_current_active_user)
):
    added = auth.create_user(user)
    if added:
        return "user added"
    else:
        raise LakehouseShareException(
            status_code=409,
            message="Conflict: User already exists please add unique user",
        )


@auth_router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@auth_router.get("/users")
async def list_users(current_user: User = Depends(get_current_active_user)):
    userslist = auth.list_users()
    return userslist
