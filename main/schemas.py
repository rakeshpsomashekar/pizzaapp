from pydantic import BaseModel
from typing import List,Optional
from datetime import datetime

class User(BaseModel):
    id:Optional[int]=None
    name:str
    mobile:int
    address:str
    email:str
    password:str
    role:str
    is_available:bool


class UserResponse(BaseModel):
    name:str
    mobile:int
    address:str
    email:str
    role:str
    class Config:
        orm_mode=True

class Pizza(BaseModel):
    name:str
    description:str
    category:str
    price:float
    availability:bool


class PizzaResponse(Pizza):
    id:int

    class Config:
        orm_mode=True

class OrderItem(BaseModel):
    
    pizza_id:int
    quantity:int
    price:int

# class OrderItemUpdate(BaseModel):
#     quantity:Optional[int]=None
#     price:Optional[float]=None

class OrderItemResponse(OrderItem):
    id:int
    order_id:int
    class Config:
        orm_mode=True

class Order(BaseModel):
    customer_id:int
    items:List[OrderItem]

class OrderResponse(BaseModel):
    id:int
    customer_id:int
    delivery_partner_id:Optional[int]
    delivery_address:str
    items:List[OrderItemResponse]
    total_price:int
    status:str
    class Config:
        orm_mode=True

class Payment(BaseModel):
    order_id:int
    payment_type:str
    payment_date:datetime
    price:int

class PaymentUpdate(BaseModel):
    payment_type:Optional[str]=None
    price:Optional[int]=None

class PaymentResponse(Payment):
    id:int
    class Config:
        orm_mode=True

# class Delivery(BaseModel):
#     order_id:int
#     delivery_partner_id:int
#     start_time:datetime
#     end_time:Optional[datetime]
#     status:str
#     comment:Optional[str]=None

# class DeliveryUpdate(BaseModel):
#     status:Optional[str]=None
#     comment:Optional[str]=None

# class DeliveryResponse(Delivery):
#     id:int
#     class Config:
#         orm_mode=True

class CartItem(BaseModel):
    pizza_id:int
    quantity:int


class CartItemUpdate(BaseModel):
    quantity:Optional[int]=None

class CartItemResponse(CartItem):
    id:int
    user_id:int
    price:int
    class Config:
        orm_mode=True

class Rating(BaseModel):
    order_id:int
    order_rating:int
    order_comment:Optional[str]=None
    delivery_partner_rating:int
    


class RatingResponse(Rating):
    id:int
    order_id:int
    user_id:int
    class Config:
        orm_mode=True

class DeliveryStatus(BaseModel):
    status:str

class DeliveryComment(BaseModel):
    status:str="completed"
    comment:Optional[str]=None

class DeliveryResponse(BaseModel):
    id:int
    order_id:int
    delivery_partner_id:int
    start_time:datetime
    end_time:Optional[datetime]=None
    status:str
    Delivery_address:str
    comment:Optional[str]=None
    class Config:
        orm_mode=True

class Token(BaseModel):
    access_token:str
    token_type:str

    class Config:
        orm_mode=True
    
class TokenData(BaseModel):
    email:str

    