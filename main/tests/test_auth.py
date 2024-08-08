import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from .. import models,schemas
from ..database import get_db,Base
from ..app import app

from main.routers.auth import create_access_token
from datetime import datetime,timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

testengine=create_engine("sqlite:///./test.db",connect_args={"check_same_thread":False})
TestingSessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=testengine)

def test_get_db():
    try:
        db=TestingSessionLocal()
        yield db
    finally:
        db.close()

if not hasattr(app,"dependency_overrides"):
    app.dependency_overrides={}

app.dependency_overrides[get_db]=test_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=testengine)
    yield TestClient(app)

#register_user testing
def test_register_user(client):
    response=client.post("/auth/register",json={
        "name":"delivery2",
        "mobile":9898989898,
        "address": "vtp",
        "email": "delivery2@gmail.com",
        "password": "delivery2",
        "role": "delivery_partner","is_available":True
    })
    assert response.status_code == 200
    data=response.json()
    assert data["email"] == "delivery2@gmail.com"
    assert data["name"] == "delivery2"

#valid login_user testing
def test_login_user(client):
    
    response=client.post('/auth/login',data={
        "username":"tester@gmail.com","password":"tester"
    })

    assert response.status_code == 200
    data=response.json()
    assert "access_token" in data and "token_type" in data
    assert data["token_type"]=="Bearer"

#invalid login testing
def test_negative_login_user(client):
    
    response=client.post('/auth/login',data={
        "username":"tester@gmail.com","password":"password"
    })

    assert response.status_code == 401
    data=response.json()
    assert data["detail"]=="incorrect credentials"


#current user testing
def test_get_current_user(client):

    log_response=client.post('/auth/login',data={
        "username":"tester@gmail.com","password":"tester"
    })
    assert log_response.status_code == 200
    token=log_response.json()['access_token']
    
    response=client.get('/auth/user',headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"]=="tester@gmail.com"

