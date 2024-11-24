from fastapi import APIRouter, Depends, HTTPException
from mongoengine import DoesNotExist, ValidationError, NotUniqueError
from typing import List
from schemas.locations import LocationSchema, LocationCreate
from models.models import User, Location as LocationModel
from utils.auth_utils import get_current_user
import logging
import traceback

router = APIRouter(prefix="/api/v3")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/locations", response_model=List[LocationSchema])
async def get_user_locations(current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"Fetching locations for user: {current_user.id}")
        user_locations = LocationModel.objects(user_id=current_user.id)
        logger.info(f"Retrieved {len(user_locations)} locations for user: {current_user.id}")
        return [LocationSchema(
            id=str(location.id),
            name=location.name,
            latitude=location.latitude,
            longitude=location.longitude,
            description=location.description,  # New property
            user_id=str(current_user.id),
            created_at=location.created_at
        ) for location in user_locations]
    except Exception as e:
        logger.error(f"Error fetching locations for user {current_user.id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="An error occurred while fetching locations")

@router.post("/locations", response_model=LocationSchema)
async def create_location(location: LocationCreate, current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"Creating new location for user: {current_user.id}")
        location_data = location.dict()
        db_location = LocationModel(**location_data, user_id=current_user.id)
        db_location.save()
        logger.info(f"Location created successfully for user: {current_user.id}")
        return LocationSchema(
            id=str(db_location.id),
            name=db_location.name,
            latitude=db_location.latitude,
            longitude=db_location.longitude,
            description=db_location.description,  # New property
            user_id=str(current_user.id),
            created_at=db_location.created_at
        )
    except NotUniqueError:
        logger.error(f"Unique constraint violation for user {current_user.id}")
        raise HTTPException(status_code=400, detail="Location with the same latitude and longitude already exists.")
    except ValidationError as e:
        logger.error(f"Validation error creating location for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data provided.")
    except Exception as e:
        logger.error(f"Unexpected error creating location for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.put("/locations/{location_id}", response_model=LocationSchema)
async def update_location(location_id: str, location: LocationCreate, current_user: User = Depends(get_current_user)):
    logger.info(f"Updating location ID: {location_id} for user: {current_user.id}")
    try:
        db_location = LocationModel.objects.get(id=location_id, user_id=str(current_user.id))
        db_location.update(**location.dict())
        db_location.reload()
        logger.info(f"Location ID {location_id} updated successfully for user: {current_user.id}")
        return LocationSchema(
            id=str(db_location.id),
            name=db_location.name,
            latitude=db_location.latitude,
            longitude=db_location.longitude,
            description=db_location.description,  # New property
            user_id=str(current_user.id),
            created_at=db_location.created_at
        )
    except DoesNotExist:
        logger.warning(f"Location ID {location_id} not found for user: {current_user.id}")
        raise HTTPException(status_code=404, detail="Location not found.")
    except ValidationError as e:
        logger.error(f"Validation error updating location ID {location_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data provided.")
    except Exception as e:
        logger.error(f"Unexpected error updating location ID {location_id} for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.delete("/locations/{location_id}", status_code=204)
async def delete_location(location_id: str, current_user: User = Depends(get_current_user)):
    logger.info(f"Attempting to delete location ID: {location_id} for user: {current_user.id}")
    try:
        db_location = LocationModel.objects.get(id=location_id, user_id=str(current_user.id))
        db_location.delete()
        logger.info(f"Location ID {location_id} deleted successfully for user: {current_user.id}")
    except DoesNotExist:
        logger.warning(f"Location ID {location_id} not found for user: {current_user.id}")
        raise HTTPException(status_code=404, detail="Location not found.")
        

@router.get("/locations/count", response_model=int)
async def get_locations_count(current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"Counting locations for user: {current_user.id}")
        count = LocationModel.objects(user_id=current_user.id).count()
        logger.info(f"User {current_user.id} has {count} locations")
        return count
    except Exception as e:
        logger.error(f"Error counting locations for user {current_user.id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="An error occurred while counting locations")