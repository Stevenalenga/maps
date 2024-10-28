from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import schemas, crud
from database import get_db

router = APIRouter()
@router.post("/", response_model=schemas.Location)
def create_location(location: schemas.LocationCreate, user_id: int, db: Session = Depends(get_db)):
    return crud.create_location(db=db, location=location, user_id=user_id)

@router.get("/", response_model=List[schemas.Location])
def read_locations(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    locations = crud.get_locations(db=db, skip=skip, limit=limit)
    return locations
