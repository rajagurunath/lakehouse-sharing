import base64
import math
from typing import Any, Callable, Generic, Optional, Sequence, TypeVar

from fastapi import Query
from fastapi.exceptions import HTTPException
from fastapi_pagination import Params
from fastapi_pagination.api import _ctx_var_with_reset, _items_val
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from fastapi_pagination.types import AdditionalData
from fastapi_pagination.utils import verify_params
from pydantic import BaseModel, conint
from starlette.requests import Request

T = TypeVar("T")


def encode_token(offsetParams, otherparams):
    next_token = "{},{}".format(offsetParams.offset + 1, ",".join(otherparams))
    print("encode_token", next_token)
    next_token = base64.urlsafe_b64encode(next_token.encode()).decode()
    return next_token


def decode_token(token_string):
    page_id = base64.urlsafe_b64decode(token_string).decode().split(",")[0]
    if page_id:
        page_id = int(page_id)
    else:
        page_id = 0
    return page_id


def validate_params(params, other_params: str):
    params_from_token = base64.urlsafe_b64decode(params).decode().split(",")[1:]
    if len(params_from_token) == len(other_params):
        for l, r in zip(params_from_token, other_params):
            if l == r:
                continue
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Token Params and Params \
                            from APIs was not equal {} ! = {}".format(
                        l, r
                    ),
                )
    else:
        raise HTTPException(
            status_code=400,
            detail="Number of decoded token params and \
                             given params length was not equal {} ! = {}".format(
                len(params_from_token), len(other_params)
            ),
        )


class SingleTokenParams(BaseModel, AbstractParams):
    maxResults: int = Query(50, ge=1, le=100, description="maxResults")
    next_token: str = Query("", description="Next Token", include_in_schema=False)

    def to_raw_params(self) -> RawParams:
        page_id = decode_token(self.next_token)
        return RawParams(limit=self.maxResults, offset=page_id)


class SingleTokenPagination(AbstractPage[T], Generic[T]):
    items: Sequence[T]
    next_token: Optional[str] = None
    __params_type__ = SingleTokenParams

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        total: int,
        params: AbstractParams,
        # request: Request
        **kwargs: Any,
    ):
        if not isinstance(params, SingleTokenParams):
            raise ValueError("Page should be used with Params")

        other_params = kwargs.get("other_params", [])
        if params.next_token:
            validate_params(params.next_token, other_params)
        offsetParams = params.to_raw_params()
        if offsetParams.offset + offsetParams.limit < total:
            next_token = encode_token(offsetParams, other_params)
        else:
            next_token = None

        return cls(
            items=items,
            total=total,
            params=params,
            next_token=next_token,
            **kwargs,
        )


def create_page(
    items: Sequence[T],
    total: Optional[int] = None,
    params: Optional[AbstractParams] = None,
    **kwargs: Any,
) -> AbstractPage[T]:
    kwargs["params"] = params

    if total is not None:  # temporary to support old signature
        kwargs["total"] = total

    with _ctx_var_with_reset(_items_val, items):
        return SingleTokenPagination.create(items=items, **kwargs)


def paginate(
    sequence: Sequence[T],
    params: Optional[AbstractParams] = None,
    length_function: Callable[[Sequence[T]], int] = len,
    *,
    additional_data: AdditionalData = {},
) -> AbstractPage[T]:
    params, raw_params = verify_params(params, "limit-offset")
    return create_page(
        sequence[raw_params.offset : raw_params.offset + raw_params.limit],
        length_function(sequence),
        params,
        **(additional_data or {}),
    )
