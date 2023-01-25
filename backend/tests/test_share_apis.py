import os
import sys

from fastapi.testclient import TestClient

os.environ["db_url"] = "sqlite:///tests/test_database.sqlite"
sys.path.append("app/")
print(sys.path)
from unittest import mock

import app.db.queries
import pytest
from app.models.auth import UserInDB
from app.routers.share import Query, get_current_active_user
from sqlmodel import Session, SQLModel, create_engine

from .mock_results import *


def skip_auth():
    user = UserInDB(
        name="test_users",
        id="3bb1ba30d5ea466e931a1fad256215c2",
        email="abc@oss.com",
        encrypted_password="encrypted###***",
    )
    return user


PREFIX = "/delta-sharing"


@pytest.fixture()
def client():
    from app.main import server

    server.dependency_overrides[get_current_active_user] = skip_auth
    with TestClient(server) as test_client:
        yield test_client


def test_list_share(client):
    response = client.get(f"{PREFIX}/shares")
    print(response.text)
    assert response.status_code == 200
    assert response.json()["items"] == ListShareResult


def test_get_share(client):
    response = client.get(f"{PREFIX}/shares/delta_share1")
    print(response.text)
    assert response.status_code == 200
    assert response.json()["share"] == ShareResult


def test_list_schema(client):
    response = client.get(f"{PREFIX}/shares/delta_share1/schemas")
    print(response.text)
    assert response.status_code == 200
    assert response.json()["items"] == ListSchemaResult


def test_list_tables(client):
    response = client.get(f"{PREFIX}/shares/iceberg_share/schemas/tripsdb/tables")
    print(response.text)
    assert response.status_code == 200
    assert response.json()["items"] == ListTableResult


def test_list_all_tables(client):
    response = client.get(f"{PREFIX}/shares/delta_share2/schemas/all-tables")
    print(response.text)
    assert response.status_code == 200
    assert response.json()["items"] == ListAllTableResult
