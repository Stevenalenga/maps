from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from Schemas.locations import LocationSchema, LocationCreate
from database import get_db
from models import User
from models import Location as LocationModel
from sqlalchemy.exc import SQLAlchemyError
import logging
from fastapi.logger import logger as fastapi_logger
from Utils.oauth2 import get_current_user
import traceback

router = APIRouter(prefix="/api/v2")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




@router.get("/locations", response_model=List[LocationSchema])
async def get_user_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Fetching locations for user: {current_user.id}")
        user_locations = db.query(LocationModel).filter(LocationModel.user_id == current_user.id).all()
        logger.info(f"Retrieved {len(user_locations)} locations for user: {current_user.id}")
        return user_locations
    except Exception as e:
        logger.error(f"Error fetching locations for user {current_user.id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="An error occurred while fetching locations")

@router.post("/locations", response_model=LocationSchema)
async def create_location(
    location: LocationCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Creating new location for user: {current_user.id}")
        location_data = location.model_dump()
        db_location = LocationModel(**location_data, user_id=current_user.id)
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        logger.info(f"Location created successfully for user: {current_user.id}")
        return db_location
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating location for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the location")
    except Exception as e:
        logger.error(f"Unexpected error creating location for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    return locations
