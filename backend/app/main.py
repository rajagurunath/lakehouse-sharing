import os

from app.utilities.exceptions import add_exception_handler
from db.queries import create_db_and_tables
from fastapi import FastAPI
from routers.admin import admin
from routers.auth import auth_router
from routers.share import share_router

TABLE_FORMAT = os.environ.get("TABLE_FORMAT", "delta")
server = FastAPI(title=f"Lakehouse-sharing - ({TABLE_FORMAT})")


@server.on_event("startup")
async def startup_event():
    print("starting db ...")
    create_db_and_tables()


add_exception_handler(server=server)
server.include_router(auth_router)
server.include_router(admin)
server.include_router(share_router)
