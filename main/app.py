from fastapi import FastAPI

from .database import engine,Base
from .routers import auth,admin,customer,delivery

app=FastAPI()

Base.metadata.create_all(engine)

app.include_router(auth.router,prefix='/auth')




app.include_router(admin.router,prefix='/admin')
app.include_router(customer.router,prefix='/customer')
app.include_router(delivery.router,prefix='/delivery')

@app.get('/')
def read_root():
    return {"message":"welcome to the pizza delivery API"}
