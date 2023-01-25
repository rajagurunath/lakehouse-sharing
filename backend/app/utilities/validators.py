from typing import Dict, List

from app.db.queries import Query
from app.models.auth import UserInDB
from app.securities.user_auth import get_current_active_user
from app.utilities.exceptions import LakehouseShareException
from fastapi import Depends, status

query = Query()


def validate_share(share, current_user: UserInDB = Depends(get_current_active_user)):
    # share = kwargs.get("share",None)
    # schema = kwargs.get("schema",None)
    # table = kwargs.get("table",None)
    exist = query.check_schema_and_table_existance(share)
    if exist:
        authorized = query.check_user_permission(current_user.id, share=share)
        if authorized:
            return current_user, share
        else:
            raise LakehouseShareException(
                status_code=status.HTTP_403_FORBIDDEN,
                message=f"User {current_user.name} does not have permission to access {share}",
            )
    else:
        raise LakehouseShareException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Required share {share} was not available in backend",
        )


def validate_share_and_schema(
    share, schema, current_user: UserInDB = Depends(get_current_active_user)
):
    # share = kwargs.get("share",None)
    # schema = kwargs.get("schema",None)
    # table = kwargs.get("table",None)
    exist = query.check_schema_and_table_existance(share, schema)
    if exist:
        return current_user, share, schema
    else:
        raise LakehouseShareException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Required share {share} and {schema} was not available in backend",
        )


def validate_share_and_schema_and_table(
    share, schema, table, current_user: UserInDB = Depends(get_current_active_user)
):
    # share = kwargs.get("share",None)
    # schema = kwargs.get("schema",None)
    # table = kwargs.get("table",None)
    exist = query.check_schema_and_table_existance(share, schema, table)
    if exist:
        return current_user, share, schema, table
    else:
        raise LakehouseShareException(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"Required share {share} and {schema} was not available in backend",
        )
