from fastapi import HTTPException, Depends, APIRouter, Query
from fastapi.params import Body
from ..database import get_db
from sqlalchemy.orm import Session
from ..schemas import User, ResponseUser, Car, CarSellOffer
from passlib.context import CryptContext
from typing import List
from .. import models, oauth2, utils

router = APIRouter(
    tags=['cars'],
    prefix="/cars"
)

@router.post("/", status_code = 201)
def create_car(car : Car, db : Session = Depends(get_db), user : User = Depends(oauth2.get_current_user)) :
    new_car = models.Car(**car.dict())
    print(user.id)
    new_car.owner_id = user.id
    print(new_car)
    
    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car

@router.get("/all", response_model=List[Car])
def get_cars(db : Session = Depends(get_db)) :
    cars = db.query(models.Car).all()
    return cars

@router.get("/mycars", response_model = List[Car])
def get_mycars(db : Session = Depends(get_db), user : User = Depends(oauth2.get_current_user)) :
    cars = db.query(models.Car).filter(models.Car.owner_id == user.id).all()
    return cars

@router.post("/buyer/offer", status_code = 201)
def create_offer(offer : CarSellOffer, db : Session = Depends(get_db), user : User = Depends(oauth2.get_current_user)) :
    car = db.query(models.Car).filter(models.Car.id == offer.car_id).first()
    # if car.owner_id == user.id :
    #     raise HTTPException(status_code=400, detail="You can't make an offer on your own car")
    new_offer = models.CarSellOffer(**offer.dict())
    new_offer.buyer_id = user.id
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)
    return new_offer



@router.get("/offer/{car_id}", status_code = 200)
def get_my_car_offers(car_id : int, db : Session = Depends(get_db), user : User = Depends(oauth2.get_current_user)) :
    offers = db.query(models.CarSellOffer).filter(models.CarSellOffer.car_id == car_id).all()
    return offers

# seller updates offer status
@router.put("/offer/{offer_id}", status_code = 200)
def update_offer(offer_id : int, status : str, db : Session = Depends(get_db), user : User = Depends(oauth2.get_current_user)) :
    offer = db.query(models.CarSellOffer).filter(models.CarSellOffer.id == offer_id).first()
    if offer.buyer_id != user.id :
        raise HTTPException(status_code=400, detail="You can't update this offer")
    offer.status = status
    db.commit()
    db.refresh(offer)
    return offer



# buyer updates offer status
@router.put("/offer/{offer_id}/buyer", status_code = 200)
def update_offer(offer_id : int, status : str, db : Session = Depends(get_db), user : User = Depends(oauth2.get_current_user)) :
    offer = db.query(models.CarSellOffer).filter(models.CarSellOffer.id == offer_id).first()
    if offer.buyer_id != user.id :
        raise HTTPException(status_code=400, detail="You can't update this offer")
    offer.buyer_status = status
    if status == "accepted" and offer.status == "accepted":
        car = db.query(models.Car).filter(models.Car.id == offer.car_id).first()
        car.sold = True
        db.commit()
        db.refresh(car)
        return {"message" : "sold"}

    db.commit()
    db.refresh(offer)
    return offer


@router.get("/{car_id}", response_model = Car)
def get_cars(car_id : int, db : Session = Depends(get_db)) :
    car = db.query(models.Car).filter(models.Car.id == car_id).first()
    return car

