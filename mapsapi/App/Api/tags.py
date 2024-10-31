from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import mapsapi.App.Schemas.schemas as schemas, crud
from database import get_db
from typing import List  # Add this import

router = APIRouter(prefix="/api/v2")

@router.post("/", response_model=schemas.Tag)
def create_tag(tag: schemas.TagCreate, db: Session = Depends(get_db)):
    db_tag = crud.create_tag(db=db, tag=tag)
    return db_tag

@router.get("/", response_model=List[schemas.Tag])
def read_tags(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    tags = crud.get_tags(db=db, skip=skip, limit=limit)
    return tags
