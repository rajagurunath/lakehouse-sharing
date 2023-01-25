from app.utilities.exceptions import LakehouseShareException
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from securities.jwt_utils import *

auth = UserCatalog()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = LakehouseShareException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        message="Unauthorized User",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = auth.get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise LakehouseShareException(status_code=403, message="Inactive user")
    return current_user
