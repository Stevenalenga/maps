from fastapi import APIRouter, Depends, HTTPException
from mongoengine import DoesNotExist, ValidationError, NotUniqueError
from typing import List
from schemas.locations import LocationSchema, LocationCreate
from models.models import User, Location as LocationModel, Fact, Tag
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
            description=location.description,  
            user_id=str(current_user.id),
            created_at=location.created_at,
            tags=[tag.name for tag in location.tags]  # Add this line
        ) for location in user_locations]
    except Exception as e:
        logger.error(f"Error fetching locations for user {current_user.id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="An error occurred while fetching locations")

@router.post("/locations", response_model=LocationSchema)
async def create_location(location: LocationCreate, current_user: User = Depends(get_current_user)):
    try:
        logger.info(f"Creating new location for user: {current_user.id}")
        tag_objects = [Tag.objects.get(name=tag) for tag in location.tags]
        new_location = LocationModel(
            name=location.name,
            latitude=location.latitude,
            longitude=location.longitude,
            description=location.description,
            user_id=current_user,
            tags=tag_objects  # Add this line
        )
        new_location.save()

        # Create a corresponding Fact
        new_fact = Fact(
            description=new_location.description,
            location_id=new_location,
            user_id=current_user
        )
        new_fact.save()

        logger.info(f"Location created with ID: {new_location.id} for user: {current_user.id}")
        return LocationSchema(
            id=str(new_location.id),
            name=new_location.name,
            latitude=new_location.latitude,
            longitude=new_location.longitude,
            description=new_location.description,
            user_id=str(current_user.id),
            created_at=new_location.created_at,
            tags=[tag.name for tag in new_location.tags]  # Add this line
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
        existing_location = LocationModel.objects.get(id=location_id, user_id=current_user.id)
        existing_location.name = location.name
        existing_location.latitude = location.latitude
        existing_location.longitude = location.longitude
        existing_location.description = location.description
        existing_location.tags = [Tag.objects.get(name=tag) for tag in location.tags]  # Add this line
        existing_location.save()

        # Update corresponding Facts
        facts = Fact.objects(location_id=existing_location.id)
        for fact in facts:
            fact.description = existing_location.description
            fact.save()

        logger.info(f"Location updated with ID: {existing_location.id} for user: {current_user.id}")
        return LocationSchema(
            id=str(existing_location.id),
            name=existing_location.name,
            latitude=existing_location.latitude,
            longitude=existing_location.longitude,
            description=existing_location.description,
            user_id=str(current_user.id),
            created_at=existing_location.created_at,
            tags=[tag.name for tag in existing_location.tags]  # Add this line
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