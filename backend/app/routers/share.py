import os

from app.conf import Config
from app.core import get_table_format_client
from app.core.base import BaseTableFormat
from app.db.queries import Query
from app.models.auth import User
from app.models.common import QueryModel, Share
from app.models.response import GetShareResponse, SchemaResponse, TableResponse
from app.securities.user_auth import *
from app.utilities.exceptions import LakehouseShareException
from app.utilities.pagination import (
    SingleTokenPagination,
    SingleTokenParams,
    encode_token,
)
from app.utilities.pagination import paginate as custom_paginate
from app.utilities.responses import common_responses
from app.utilities.validators import (
    validate_share,
    validate_share_and_schema,
    validate_share_and_schema_and_table,
)
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi_pagination import Page, Params, add_pagination, paginate
from starlette.responses import JSONResponse, StreamingResponse

config = Config()
PREFIX = config.get("endpoint")
share_router = APIRouter(prefix=PREFIX, responses=common_responses, tags=["sharing"])

query = Query()
LakeHouse: BaseTableFormat = get_table_format_client(
    os.environ.get("TABLE_FORMAT", "delta")
)()


@share_router.get("/shares", response_model=SingleTokenPagination[Share], responses={})
def list_shares(
    params: SingleTokenParams = Depends(),
    current_user: User = Depends(get_current_active_user),
):
    # shares = config.get("shares")
    # print(shares)
    shares = query.list_shares(current_user.id)
    print(shares)
    return custom_paginate(shares, params)


@share_router.get("/shares/{share}", response_model=GetShareResponse)
def get_share(user_share=Depends(validate_share)):
    # shares = config.get("shares")
    user, share = user_share
    shares = query.get_share(share=share, user_id=user.id)
    return {"share": shares}


@share_router.get(
    "/shares/{share}/schemas", response_model=SingleTokenPagination[SchemaResponse]
)
def list_schema(
    user_share=Depends(validate_share), params: SingleTokenParams = Depends()
):
    user, share = user_share
    schemas = query.list_schemas(share)
    return custom_paginate(
        schemas, params=params, additional_data={"other_params": [share]}
    )


# list(filter(lambda s: s['name']==share,shares))[0]


@share_router.get(
    "/shares/{share}/schemas/{schema}/tables",
    response_model=SingleTokenPagination[TableResponse],
)
def list_tables(
    share_and_schema=Depends(validate_share_and_schema),
    params: SingleTokenParams = Depends(),
):
    user, share, schema = share_and_schema
    schemas = query.list_tables(share, schema=schema)
    return custom_paginate(
        schemas, params=params, additional_data={"other_params": [share, schema]}
    )


@share_router.get(
    "/shares/{share}/schemas/all-tables",
    response_model=SingleTokenPagination[TableResponse],
)
def list_all_tables(
    user_share=Depends(validate_share),
    params: SingleTokenParams = Depends(),
):
    user, share = user_share
    schemas = query.list_all_tables(share, user.id)
    return custom_paginate(
        schemas, params=params, additional_data={"other_params": [share]}
    )


@share_router.head("/shares/{share}/schemas/{schema}/tables/{table}")
def get_table_version(share_schema_table=Depends(validate_share_and_schema_and_table)):
    try:
        user, share, schema, table = share_schema_table
        return JSONResponse(
            {},
            headers={
                "delta-table-version": LakeHouse.table_version(
                    share, schema=schema, table_name=table
                )
            },
        )
    except Exception as e:
        raise LakehouseShareException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e)
        )


@share_router.get("/shares/{share}/schemas/{schema}/tables/{table}/metadata")
async def get_table_metadata(
    share_schema_table_user=Depends(validate_share_and_schema_and_table),
):

    try:
        user, share, schema, table = share_schema_table_user

        response = StreamingResponse(
            LakeHouse.table_metadata(share=share, schema=schema, table_name=table),
            headers={
                "delta-table-version": LakeHouse.table_version(
                    share, schema=schema, table_name=table
                )
            },
            media_type="application/json",
        )
        return response
    except Exception as e:
        raise LakehouseShareException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e)
        )


@share_router.post("/shares/{share}/schemas/{schema}/tables/{table}/query")
async def query_table_files(
    queryM: QueryModel,
    share_schema_table_user=Depends(validate_share_and_schema_and_table),
):
    try:
        user, share, schema, table = share_schema_table_user
        token_lifetime = auth.get_token_lifetime(user.id)
        response = StreamingResponse(
            LakeHouse.file_details(
                share,
                schema=schema,
                table_name=table,
                predicateHints=queryM.predicateHints,
                limitHint=queryM.limitHint,
                version=queryM.version,
                file_expiry=token_lifetime,
            ),
            headers={
                "delta-table-version": LakeHouse.table_version(
                    share, schema=schema, table_name=table
                )
            },
            media_type="application/json",
        )
        return response
    except Exception as e:
        raise LakehouseShareException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=str(e)
        )
