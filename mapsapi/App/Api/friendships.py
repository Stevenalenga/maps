from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas, crud
from database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Friendship)
def create_friendship(friendship: schemas.FriendshipCreate, db: Session = Depends(get_db)):
    db_friendship = crud.create_friendship
