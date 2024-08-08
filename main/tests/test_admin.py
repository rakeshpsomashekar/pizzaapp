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
    return schemas.User(id=1,name="tester",email="tester@gmail.com",role="admin",mobile=9898,address="vtp",password="tester",is_available=True)

app.dependency_overrides[get_db]=test_get_db
app.dependency_overrides[get_current_user]=new_current_user

@pytest.fixture(scope="module")
def client():
    # Base.metadata.create_all(bind=testengine)
    yield TestClient(app)

def test_create_pizza(client):
    response=client.post("/admin/pizzas/",json={
  "name": "onion",
  "description": "oni0n spicy",
  "category": "small",
  "price": 50,
  "availability": True
})
    assert response.status_code == 200
    data=response.json()
    assert data["name"] == "onion"
    assert data["price"] == 50


def test_update_pizza(client):
    response=client.put("/admin/pizzas/3",json={"name": "mus","description": "paneer with cheeeeese","category": "big","price": 100,"availability": True})
    assert response.status_code == 200
    data=response.json()
    assert data["name"] == "mus"
    
def test_delete_pizza(client):
    response=client.delete("/admin/pizzas/2")
    assert response.status_code == 200

