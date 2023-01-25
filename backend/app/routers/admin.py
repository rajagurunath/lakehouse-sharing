from app.conf import Config
from app.db.queries import AdminQuery
from app.models.admin import (
    PermissionModel,
    SchemaModel,
    ShareModel,
    TableModel,
    TokenLifetime,
)
from app.securities.user_auth import *
from app.utilities import get_random_uuid
from fastapi import APIRouter, Depends

admin = APIRouter(prefix="/admin", tags=["admin"])

query = AdminQuery()


@admin.post("/share")
def create_share(share: ShareModel, current_user=Depends(get_current_user)):
    # shares = config.get("shares")
    query.create_share(share)
    return f"Share {share.name} was created successfully"


@admin.post("/schema")
def create_schema(schema: SchemaModel, current_user=Depends(get_current_user)):
    # shares = config.get("shares")
    query.create_schema(schema)
    return f"Schema {schema.name} was created successfully"


@admin.post("/table")
def create_table(table: TableModel, current_user=Depends(get_current_user)):
    # shares = config.get("shares")
    query.create_table(table)
    return f"Table {table.table_name} was created successfully"


@admin.post("/link")
def link_resources(resources: PermissionModel):
    query.link_resources(resources)
    return f"Resources linked successfully"


@admin.post("/lifetime")
def update_token_lifetime(lifetime: TokenLifetime):
    user_id = query.get_id_by_user(lifetime.username)
    print("user_id", user_id)
    if user_id:
        query.add_lifetime(user_id=user_id, expiry=lifetime.expiry)
        return "expiry updated successfully"
    else:
        raise LakehouseShareException(status_code=402, message="Failed")


@admin.get("/token/{user_id}", response_model=Token)
async def sharing_token(user_id: str, current_user=Depends(get_current_user)):
    token_lifetime = auth.get_token_lifetime(user_id)

    username = auth.get_username_by_id(user_id=user_id)
    if username is None:
        raise LakehouseShareException(
            status_code=404, message=f"User ID {user_id} not found"
        )
    print("token_lifetime", token_lifetime)
    token_expiry = token_lifetime if token_lifetime else ACCESS_TOKEN_EXPIRE_MINUTES
    access_token_expires = timedelta(seconds=token_expiry)
    access_token = auth.create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
