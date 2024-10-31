from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import mapsapi.App.Schemas.schemas as schemas, crud
from database import get_db

router = APIRouter(prefix="/api/v2")

@router.post("/", response_model=schemas.Friendship)
def create_friendship(friendship: schemas.FriendshipCreate, db: Session = Depends(get_db)):
    db_friendship = crud.create_friendship
