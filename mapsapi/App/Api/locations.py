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
        location_data = location.dict()  # Use dict() instead of model_dump()
        db_location = LocationModel(**location_data, user_id=current_user.id)
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        logger.info(f"Location created successfully for user: {current_user.id}")
        return db_location  # Return the created location
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating location for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the location")
    except Exception as e:
        logger.error(f"Unexpected error creating location for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.put("/locations/{location_id}", response_model=LocationSchema)  # Route for updating a location
async def update_location(
    location_id: int,
    location: LocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Updating location ID: {location_id} for user: {current_user.id}")
    
    # Find the location to update
    db_location = db.query(LocationModel).filter(LocationModel.id == location_id, LocationModel.user_id == current_user.id).first()
    
    if db_location is None:
        logger.warning(f"Location ID {location_id} not found for user: {current_user.id}.")
        raise HTTPException(status_code=404, detail="Location not found.")
    
    # Update the location's attributes
    db_location.name = location.name
    db_location.latitude = location.latitude
    db_location.longitude = location.longitude
    
    try:
        db.commit()
        db.refresh(db_location)  # Refresh to get the updated data
        logger.info(f"Location ID {location_id} updated successfully for user: {current_user.id}.")
        return db_location
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating location ID {location_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the location.")
    except Exception as e:
        logger.error(f"Unexpected error updating location ID {location_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")


@router.delete("/locations/{location_id}", status_code=204)  # Route for deleting a location
async def delete_location(
    location_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    logger.info(f"Attempting to delete location ID: {location_id} for user: {current_user.id}")
    
    # Find the location to delete
    db_location = db.query(LocationModel).filter(LocationModel.id == location_id, LocationModel.user_id == current_user.id).first()
    
    if db_location is None:
        logger.warning(f"Location ID {location_id} not found for user: {current_user.id}.")
        raise HTTPException(status_code=404, detail="Location not found.")
    

