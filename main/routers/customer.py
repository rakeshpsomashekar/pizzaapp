from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas,models
from .auth import get_current_user
from ..database import get_db

router=APIRouter()

@router.get("/pizzas/",response_model=List[schemas.PizzaResponse])
def get_pizzas(db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="customer":
        raise HTTPException(status_code=403,detail="not enough permissions")
    pizzas=db.query(models.Pizza).all()
    return pizzas

@router.get("/pizzas/filter",response_model=List[schemas.PizzaResponse])
def get_filtered_pizzas(category:str,db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="customer":
        raise HTTPException(status_code=403,detail="not enough permissions")
    pizzas=db.query(models.Pizza).filter(models.Pizza.category==category).all()
    return pizzas


@router.post("/cart/",response_model=schemas.CartItemResponse)
def add_to_cart(item:schemas.CartItem,db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="customer":
        raise HTTPException(status_code=403,detail="not enough permissions")
    pizza=db.query(models.Pizza).filter(models.Pizza.id==item.pizza_id).first()
    if pizza and pizza.availability :
        cart_item=db.query(models.CartItem).filter(models.CartItem.user_id==current_user.id,models.CartItem.pizza_id==item.pizza_id).first()
        if cart_item:

            cart_item.quantity+=item.quantity
            cart_item.price+=item.quantity*pizza.price
        else:
            cart_item=models.CartItem(user_id=current_user.id,pizza_id=item.pizza_id,quantity=item.quantity,price=item.quantity*pizza.price)
            db.add(cart_item)

        db.commit()
        db.refresh(cart_item)
    else:
        raise HTTPException(status_code=404,detail="pizza not found or not available")
    
    return cart_item




@router.post("/checkout/",response_model=schemas.OrderResponse)
def checkout_cart(payment_type:str,delivery_address:str,db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="customer":
        raise HTTPException(status_code=403,detail="not enough permissions")
    cart_items=db.query(models.CartItem).filter(models.CartItem.user_id==current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400,detail="Cart is empty")
    #check and create order when we checkout
    order=models.Order(customer_id=current_user.id,status="inprogress",delivery_address=delivery_address)
    db.add(order)
    db.commit()
    db.refresh(order)

    #checkout all cart items into order
    order_items=[]
    total=0
    for items in cart_items:
        order_item=models.OrderItem(
            order_id=order.id,
            pizza_id=items.pizza_id,
            quantity=items.quantity,
            price=items.price
        )
        db.add(order_item)
        order_items.append(order_item)
        total+=items.price
    #assigning delivery partner
    delivery_partner=db.query(models.User).filter(models.User.role=='delivery_partner',models.User.is_available==True).first()
    if delivery_partner:
        order.delivery_partner_id=delivery_partner.id
        delivery_partner.is_available=False
        db.add(order.delivery_partner)
    else:
        raise HTTPException(status_code=404,detail="No delivery partner available")

    #creating payment data into paymentmodel
    payment=models.Payment(order_id=order.id,price=total,payment_type=payment_type)
    db.add(payment)
    #clear all cart items
    db.query(models.CartItem).filter(models.CartItem.user_id==current_user.id).delete()

    delivery=models.Delivery(order_id=order.id,delivery_partner_id=delivery_partner.id,
                             end_time=None,status="in_progress",comment="item delivery in 50 mins")
    db.add(delivery)

    db.commit()
    db.refresh(order)
    return schemas.OrderResponse(
        id=order.id,customer_id=order.customer_id,status=order.status,delivery_address=order.delivery_address,delivery_partner_id=order.delivery_partner_id,items=[schemas.OrderItemResponse(
            id=item.id,
            order_id=item.order_id,
            pizza_id=item.pizza_id,
            quantity=item.quantity,
            price=item.price)for item in order_items],
            total_price=sum(item.price for item in order_items)
        )


@router.post("/orders/",response_model=List[schemas.OrderResponse])
def get_orders(db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="customer":
        raise HTTPException(status_code=403,detail="not enough permissions")
    orders=db.query(models.Order).filter(models.Order.customer_id==current_user.id).all()
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="orders not found")
    order_responses=[]
    for order in orders:
        order_items=db.query(models.OrderItem).filter(models.OrderItem.order_id==order.id).all()
        order_responses.append(schemas.OrderResponse(
        id=order.id,customer_id=order.customer_id,delivery_partner_id=order.delivery_partner_id,status=order.status,items=[schemas.OrderItemResponse(
            id=item.id,
            order_id=item.order_id,
            pizza_id=item.pizza_id,
            quantity=item.quantity,
            price=item.price)for item in order_items],
            total_price=sum(item.price for item in order_items)
        ))
    return order_responses



@router.post("/cartitems/",response_model=List[schemas.CartItemResponse])
def get_cart_items(db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="customer":
        raise HTTPException(status_code=403,detail="not enough permissions")
    cart_items=db.query(models.CartItem).filter(models.CartItem.user_id==current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400,detail="Cart is empty")
    return [schemas.CartItemResponse(id=item.id,user_id=item.user_id,pizza_id=item.pizza_id,quantity=item.quantity,price=item.price
                                     ) for item in cart_items]


@router.delete("/cart/{pizza_id}",response_model=schemas.CartItemResponse)
def remove_cart_pizza(pizza_id:int,db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="customer":
        raise HTTPException(status_code=403,detail="not enough permissions")
    cart_item=db.query(models.CartItem).filter(models.CartItem.user_id==current_user.id,models.CartItem.pizza_id==pizza_id).first()
    if not cart_item:
        raise HTTPException(status_code=404,detail="pizza not found in cart")
    db.delete(cart_item)
    db.commit()

    return schemas.CartItemResponse(id=cart_item.id,user_id=cart_item.user_id,pizza_id=cart_item.pizza_id,quantity=cart_item.quantity,price=cart_item.price)

@router.delete("/cart/",response_model=List[schemas.CartItemResponse])
def clear_cart(db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="customer":
        raise HTTPException(status_code=403,detail="not enough permissions")
    cart_items=db.query(models.CartItem).filter(models.CartItem.user_id==current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=404,detail="no items found in cart")
    for i in cart_items:
        db.delete(i)
    db.commit()

    return [schemas.CartItemResponse(id=item.id,user_id=item.user_id,pizza_id=item.pizza_id,quantity=item.quantity,price=item.price
                                     ) for item in cart_items]



@router.post("/delivery_rating/",response_model=schemas.RatingResponse)
def delivery_ratings(ratings:schemas.Rating,db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="customer":
        raise HTTPException(status_code=403,detail="not enough permissions")
    order=db.query(models.Order).filter(models.Order.id==ratings.order_id,models.Order.customer_id==current_user.id).first()
    if not order:
        raise HTTPException(status_code=404,detail="Order not found")
    
    delivery=db.query(models.Delivery).filter(models.Delivery.order_id==order.id).first()
    if delivery.status == 'completed':
        rating=models.Rating(user_id=current_user.id,order_id=order.id,order_rating=ratings.order_rating,order_comment=ratings.order_comment,delivery_partner_rating=ratings.delivery_partner_rating)
        db.add(rating)
        db.commit()
        db.refresh(rating)
        return rating
    else:
        raise HTTPException(status_code=404,detail="Order not deliveried")
    



