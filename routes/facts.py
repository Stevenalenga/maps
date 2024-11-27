from fastapi import APIRouter, Depends, HTTPException
from mongoengine import DoesNotExist, ValidationError
from models.models import Fact, Location, User, Tag
from utils.auth_utils import get_current_user
from typing import List
import logging
from schemas.facts import FactResponse, FactCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3")

@router.get("/locations/{location_id}/facts", response_model=List[FactResponse])
def get_facts_by_location(location_id: str, current_user: User = Depends(get_current_user)):
    logger.info(f"Fetching facts for location ID: {location_id} by user ID: {current_user.id}")
    facts = Fact.objects(location_id=location_id)
    if not facts:
        logger.warning(f"No facts found for location ID: {location_id}")
        raise HTTPException(status_code=404, detail="No facts found for this location.")
    
    location = Location.objects.get(id=location_id)
    logger.info(f"Found {len(facts)} facts for location ID: {location_id}")
    return [FactResponse(
        id=str(fact.id),
        description=fact.description,  # Get description from Location model
        location_id=str(fact.location_id.id),
        user_id=str(current_user.id),
        created_at=fact.created_at
    ) for fact in facts]

@router.post("/locations/{location_id}/facts", response_model=FactResponse)
def create_fact(location_id: str, fact: FactCreate, current_user: User = Depends(get_current_user)):
    logger.info(f"Creating fact for location ID: {location_id} by user ID: {current_user.id}")
    try:
        location = Location.objects.get(id=location_id)
    except DoesNotExist:
        logger.warning(f"Location ID: {location_id} does not exist")
        raise HTTPException(status_code=404, detail="Location not found")

    new_fact = Fact(
        description=location.description,  # Get description from Location model
        location_id=location,
        user_id=current_user
    )
    new_fact.save()
    logger.info(f"Fact created with ID: {new_fact.id} for location ID: {location_id}")
    return FactResponse(
        id=str(new_fact.id),
        description=new_fact.description,
        location_id=str(new_fact.location_id.id),
        user_id=str(current_user.id),
        created_at=new_fact.created_at
    )

@router.delete("/facts/{fact_id}", status_code=204)
def delete_fact(fact_id: str, current_user: User = Depends(get_current_user)):
    logger.info(f"Attempting to delete fact with ID: {fact_id} by user ID: {current_user.id}")
    try:
        fact = Fact.objects.get(id=fact_id, user_id=current_user)
        fact.delete()
        logger.info(f"Fact with ID: {fact_id} deleted")
    except DoesNotExist:
        logger.warning(f"Fact ID: {fact_id} does not exist or not owned by user ID: {current_user.id}")
        raise HTTPException(status_code=404, detail="Fact not found")

@router.put("/locations/{location_id}/facts/{fact_id}", response_model=FactResponse)
def update_fact(location_id: str, fact_id: str, fact: FactCreate, current_user: User = Depends(get_current_user)):
    logger.info(f"Updating fact with ID: {fact_id} for location ID: {location_id} with new description: {fact.description} by user ID: {current_user.id}")
    try:
        location_exists = Location.objects.get(id=location_id)
    except DoesNotExist:
        logger.warning(f"Location ID {location_id} does not exist.")
        raise HTTPException(status_code=404, detail="Location not found.")

    try:
        fact_to_update = Fact.objects.get(id=fact_id, location_id=location_id)
        fact_to_update.update(description=fact.description)
        fact_to_update.reload()
        logger.info(f"Fact with ID {fact_id} updated successfully for location ID: {location_id}")
        return FactResponse(
            id=str(fact_to_update.id),
            description=fact_to_update.description,
            location_id=str(fact_to_update.location_id),
            user_id=str(current_user.id),
            created_at=fact_to_update.created_at
        )
    except DoesNotExist:
        logger.warning(f"Fact with ID {fact_id} not found for location ID {location_id}")
        raise HTTPException(status_code=404, detail="Fact not found.")
    except ValidationError as e:
        logger.error(f"Validation error updating fact: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data provided.")
    except Exception as e:
        logger.error(f"Error updating fact: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the fact.")

@router.post("/facts", response_model=FactResponse)
def create_fact(description: str, location_id: str, tags: list[str], current_user: User = Depends(get_current_user)):
    try:
        location = Location.objects.get(id=location_id)
    except DoesNotExist:
        logger.warning(f"Location ID: {location_id} does not exist")
        raise HTTPException(status_code=404, detail="Location not found")

    tag_objects = [Tag.objects.get(name=tag) for tag in tags]

    new_fact = Fact(
        description=description,
        location_id=location,
        user_id=current_user,
        tags=tag_objects
    )
    new_fact.save()
    logger.info(f"Fact created with ID: {new_fact.id} for location ID: {location_id}")
    return FactResponse(
        id=str(new_fact.id),
        description=new_fact.description,
        location_id=str(new_fact.location_id.id),
        user_id=str(current_user.id),
        created_at=new_fact.created_at
    )