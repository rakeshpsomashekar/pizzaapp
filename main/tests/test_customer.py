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
    return schemas.User(id=1,name="testcustomer",email="testcustomer@gmail.com",role="customer",mobile=9898,address="vtp",password="testcostomer",is_available=True)

app.dependency_overrides[get_db]=test_get_db
app.dependency_overrides[get_current_user]=new_current_user

@pytest.fixture(scope="module")
def client():
    # Base.metadata.create_all(bind=testengine)
    yield TestClient(app)


def test_get_pizzas(client):
    response=client.get("/customer/pizzas/")
    assert response.status_code==200
    assert response.json()[0]["name"]=="Paneer"


def test_add_to_cart(client):
    response=client.post("/customer/cart",json={
  "pizza_id": 2,
  "quantity": 2 })
    assert response.status_code==200
    assert response.json()["pizza_id"]==2
    assert response.json()["quantity"]==2

def test_checkout_cart(client):
    response=client.post("/customer/checkout/",params={"payment_type":"credit_card"})
    assert response.status_code==200


def test_get_orders(client):
    response=client.post("/customer/orders/")
    assert response.status_code==200
    # assert response.json()[0]['status']=='inprogress'

def test_get_cart_items(client):
    response=client.post("/customer/cartitems/")
    assert response.status_code==200


def test_remove_cart_pizza(client):
    response=client.delete("customer/cart/1")
    assert response.status_code==200


def test_clear_cart(client):
    response=client.delete("customer/cart/")
    assert response.status_code==200

def test_delivery_rating(client):
    response=client.post("customer/delivery_rating/",json={
  "order_id": 1,
  "rating": 5,
  "comment": "delicious"
})
    assert response.status_code==200