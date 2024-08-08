import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from .. import models,schemas
from ..database import get_db,Base
from ..app import app
from ..routers.auth import get_current_user

from main.routers.auth import create_access_token
from datetime import datetime,timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .test_auth import TestingSessionLocal,testengine
def test_get_db():
    try:
        db=TestingSessionLocal()
        yield db
    finally:
        db.close()

if not hasattr(app,"dependency_overrides"):
    app.dependency_overrides={}


def new_current_user():
    return schemas.User(id=1,name="delivery",email="delivery@gmail.com",role="delivery_partner",mobile=9898,address="vtp",password="delivery",is_available=True)

app.dependency_overrides[get_db]=test_get_db
app.dependency_overrides[get_current_user]=new_current_user

@pytest.fixture(scope="module")
def client():
    yield TestClient(app)


def test_delivery_status_update(client):
    response=client.put("/delivery/deliveries/1/status",json={"status": "on_vehicle"})
    assert response.status_code==200

def test_delivery_close(client):
    response=client.put("/delivery/deliveries/1/close",json={"status": "on_vehicle","comment":"super delivery"})
    assert response.status_code==200