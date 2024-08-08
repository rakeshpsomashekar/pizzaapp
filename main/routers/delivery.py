from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from typing import List
from .. import schemas,models
from .auth import get_current_user
from ..database import get_db
from datetime import datetime
router=APIRouter()



@router.get("/deliveries/",response_model=List[schemas.DeliveryResponse])
def get_deliveries(db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="delivery_partner":
        raise HTTPException(status_code=403,detail="not enough permissions")
    deliveries=db.query(models.Delivery).filter(models.Delivery.delivery_partner_id==current_user.id).all()
    if not deliveries:
        raise HTTPException(status_code=404,detail="no deliveries found for you")

    for delivery in deliveries:
        order=db.query(models.Order).filter(models.Order.id==delivery.order_id).first()
        if not order:
            raise HTTPException(status_code=404,detail="no order delivery")

    return [schemas.DeliveryResponse(
        id=delivery.id,
        order_id=delivery.order_id,
        delivery_partner_id=delivery.delivery_partner_id,
        start_time=delivery.start_time,
        end_time=delivery.end_time,
        status=delivery.status,
        Delivery_address=order.delivery_address,
        comment=delivery.comment
    ) for delivery in deliveries]


@router.put("/deliveries/{delivery_id}/status",response_model=schemas.DeliveryResponse)
def update_delivery_status(delivery_id:int,status:schemas.DeliveryStatus,db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="delivery_partner":
        raise HTTPException(status_code=403,detail="not enough permissions")
    delivery=db.query(models.Delivery).filter(models.Delivery.id==delivery_id).first()
    
    if not delivery:
        raise HTTPException(status_code=404,detail="delivery not found")
    if delivery.status=="completed":
        raise HTTPException(status_code=403,detail="not enough permissions and delivery completed ")
    
    delivery.status=status.status
    db.commit()
    db.refresh(delivery)

    order=db.query(models.Order).filter(models.Order.id==delivery.order_id).first()

    return schemas.DeliveryResponse(
        id=delivery.id,
        order_id=delivery.order_id,
        delivery_partner_id=delivery.delivery_partner_id,
        start_time=delivery.start_time,
        end_time=delivery.end_time,
        status=delivery.status,
        Delivery_address=order.delivery_address,
        comment=delivery.comment
    )

@router.put("/deliveries/{delivery_id}/close",response_model=schemas.DeliveryResponse)
def delivery_close(delivery_id:int,delivery_close:schemas.DeliveryComment,db:Session=Depends(get_db),current_user:schemas.User=Depends(get_current_user)):
    if current_user.role !="delivery_partner":
        raise HTTPException(status_code=403,detail="not enough permissions")
    
    delivery=db.query(models.Delivery).filter(models.Delivery.id==delivery_id).first()

    if not  delivery:
        raise HTTPException(status_code=404,detail="delivery not found")
    
    if delivery.status=="completed":
        raise HTTPException(status_code=403,detail="not enough permissions delivery completed")

    delivery.status="completed"
    delivery.end_time=datetime.utcnow()
    delivery.comment=delivery_close.comment
        
    db.commit()
    db.refresh(delivery)
    
    #again makin available of a delivery partner for new orders
    user=db.query(models.User).filter(models.User.id==delivery.delivery_partner_id).first()
    if user:
        user.is_available=True
        db.commit()
        db.refresh(user)
    order=db.query(models.Order).filter(models.Order.id==delivery.order_id).first()
    
    return schemas.DeliveryResponse(
        id=delivery.id,
        order_id=delivery.order_id,
        delivery_partner_id=delivery.delivery_partner_id,
        start_time=delivery.start_time,
        end_time=delivery.end_time,
        status=delivery.status,
        Delivery_address=order.delivery_address,
        comment=delivery.comment
    )

