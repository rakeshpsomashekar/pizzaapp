from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from .auth import get_current_user
from ..database import get_db
from .. import schemas,models
router=APIRouter()


@router.post("/pizzas/",response_model=schemas.PizzaResponse)
def create_pizza(pizza:schemas.Pizza,db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)): 
    if current_user.role!="admin":
        raise HTTPException(status_code=403,detail="not enough permissions")
    new_pizza=models.Pizza(**pizza.dict())
    db.add(new_pizza)
    db.commit()
    db.refresh(new_pizza)
    return new_pizza


@router.put("/pizzas/{id}",response_model=schemas.PizzaResponse)
def update_pizza(id:int,pizza_update:schemas.Pizza,db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role!="admin":
        raise HTTPException(status_code=403,detail="not enough permissions")
    pizza=db.query(models.Pizza).filter(models.Pizza.id==id).first()
    if not pizza:
        raise HTTPException(status_code=404,detail="pizza not found")
    if pizza:
        data=pizza_update.dict()
        pizza.name=data.get('name',pizza.name)
        pizza.price=data.get('price',pizza.price)
        pizza.description=data.get('description',pizza.description)
        pizza.category=data.get('category',pizza.category)
        pizza.availability=data.get('availability',pizza.availability)
        db.commit()
        db.refresh(pizza)
        return pizza
    return None

@router.delete("/pizzas/{id}",response_model=schemas.PizzaResponse)
def delete_pizza(id:int,db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role!="admin":
        raise HTTPException(status_code=403,detail="not enough permissions")
    pizza=db.query(models.Pizza).filter(models.Pizza.id==id).first()
    if not pizza:
        raise HTTPException(status_code=404,detail="pizza not found")
    if pizza:
        db.delete(pizza)
        db.commit()
        return pizza
    return None

@router.put("/order-status/{order_id}",response_model=schemas.Order)
def update_order_status(id:int,status:str,db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="admin":
        raise HTTPException(status_code=403,detail="not enough permissions")
    order=db.query(models.Order).filter(models.Order.id==id).first()
    if not order:
        raise HTTPException(status_code=404,detail="order not found")
    order.status=status
    db.commit()
    db.refresh(order)
    order_items=db.query(models.OrderItem).filter(models.OrderItem.order_id==order.id).all()

    return schemas.OrderResponse(
        id=order.id,customer_id=order.customer_id,delivery_partner_id=order.delivery_partner_id,status=order.status,items=[schemas.OrderItemResponse(
            id=item.id,
            order_id=item.order_id,
            pizza_id=item.pizza_id,
            quantity=item.quantity,
            price=item.price)for item in order_items],
            total_price=sum(item.price for item in order_items)
    )

