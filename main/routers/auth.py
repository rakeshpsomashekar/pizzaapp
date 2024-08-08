from datetime import datetime,timedelta
from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError,jwt
from passlib.context import CryptContext

from .. import models,schemas
from ..database import get_db

SECRET_KEY="nccscsdc68vcz89"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

router=APIRouter()


def authenticate_user(db:Session,email:str,password:str):
    user=db.query(models.User).filter(models.User.email==email).first()
    print(user)
    if user is None:
        return None
    if pwd_context.verify(password,user.password):
        return user
    return None

def create_access_token(data:dict):
    to_encode=data.copy()
    exp=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":exp})
    encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

@router.post("/register/",response_model=schemas.UserResponse)
def register(user:schemas.User,db:Session=Depends(get_db)):
    user_email=db.query(models.User).filter(models.User.email==user.email).first()
    if user_email:
        raise HTTPException(status_code=400,detail="Email should be unique")
    user=models.User(name=user.name,mobile=user.mobile,password=pwd_context.hash(user.password),
                     address=user.address,role=user.role,email=user.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login",response_model=schemas.Token)
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    user=authenticate_user(db,form.username,form.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="incorrect credentials")
    access_token=create_access_token(data={"sub":user.email})
    return {"access_token":access_token,"token_type":"Bearer"}


oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.get("/user",response_model=schemas.UserResponse)
def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    error=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="incorrect credentials")
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        email:str =payload.get("sub")
        if email is None:
            raise error
    except JWTError:
        raise error
    user=db.query(models.User).filter(models.User.email==email).first()
    if user is None:
            raise error
    return user



