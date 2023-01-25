from app.models.response import CommonErrorResponse, Share
from fastapi import status


def get_response_dict(model, message):
    response = {
        "model": model,  # custom pydantic model for 200 response
        "description": message,
    }
    return response


def get_200_ok(model):
    success_response = get_response_dict(model=model, message="Success message")
    return success_response


common_responses = {
    status.HTTP_200_OK: get_200_ok(Share),
    status.HTTP_400_BAD_REQUEST: get_response_dict(
        CommonErrorResponse, "The request is malformed."
    ),
    status.HTTP_401_UNAUTHORIZED: get_response_dict(
        CommonErrorResponse,
        "The request is unauthenticated. The bearer token is missing or incorrect.",
    ),
    status.HTTP_403_FORBIDDEN: get_response_dict(
        CommonErrorResponse, "The request is forbidden from being fulfilled."
    ),
    status.HTTP_404_NOT_FOUND: get_response_dict(
        CommonErrorResponse, "The requested resource does not exist."
    ),
    status.HTTP_500_INTERNAL_SERVER_ERROR: get_response_dict(
        CommonErrorResponse,
        "The request is not handled correctly due to a server error.",
    ),
}
