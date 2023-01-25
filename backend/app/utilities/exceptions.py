from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class LakehouseShareException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


def add_exception_handler(server):
    print("Registering the exception handler")

    @server.exception_handler(LakehouseShareException)
    async def lakehouse_share_exception_handler(
        request: Request, exc: LakehouseShareException
    ):
        return JSONResponse(
            status_code=exc.status_code,
            content={"errorCode": exc.status_code, "message": exc.message},
        )

    return server
