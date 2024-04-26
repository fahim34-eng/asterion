from fastapi import FastAPI, Response, HTTPException, Depends, APIRouter, Query
from fastapi.params import Body
from ..database import get_db
from sqlalchemy.orm import Session
from ..schemas import User, ResponseUser, UpdateUser, Token
from passlib.context import CryptContext
from typing import List
from .. import models, oauth2, utils

router = APIRouter()

@router.get("/")
def home():
    return {"ping": "pong"}

@router.post("/users", status_code = 201, tags=['users'])
def create_user(user : User ,db : Session = Depends(get_db)) :
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_pass = pwd_context.hash(user.password)
    user.password = hashed_pass
    user.role = "customer"
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token = oauth2.create_access_token({ "id": new_user.id, "email": new_user.email })
    return {"access_token": access_token, "token_type": "Bearer", "id" : new_user.id, "role" : new_user.role }

@router.get("/users", response_model=List[ResponseUser], tags=['users'])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.delete("/users/{id}", response_model = ResponseUser, tags=['users'])
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return user


@router.get("/profile", response_model=ResponseUser, tags=['users'])
def get_info(db: Session = Depends(get_db), user = Depends(oauth2.get_current_user)):
    user_from_db = db.query(models.User).filter(models.User.id == user.id).first()
    user_from_db.age = utils.calculate_age(user_from_db.dob)
    return user_from_db