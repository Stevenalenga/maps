from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models import Fact, Location ,User
from database import get_db
from Utils.oauth2 import get_current_user
from typing import List
import logging
from Schemas.facts import FactResponse  ,FactCreate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2")

@router.get("/locations/{location_id}/facts", response_model=List[FactResponse])  # Use the Pydantic model here
def get_facts_by_location(
    location_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)  # Ensure user is authenticated
):
    logger.info(f"Fetching facts for location ID: {location_id} by user ID: {current_user.id}")
    
    # Query the database for facts associated with the location
    facts = db.query(Fact).filter(Fact.location_id == location_id).all()
    
    if not facts:
        logger.warning(f"No facts found for location ID: {location_id}")
        raise HTTPException(status_code=404, detail="No facts found for this location.")
    
    logger.info(f"Found {len(facts)} facts for location ID: {location_id}")
    return facts



@router.post("/locations/{location_id}/facts", response_model=FactResponse)
def create_fact(
    location_id: int, 
    fact: FactCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)  # Ensure user is authenticated
):
    logger.info(f"Creating fact for location ID: {location_id} with description: {fact.description} by user ID: {current_user.id}")
    
    # Check if the location ID exists
    location_exists = db.query(Location).filter(Location.id == location_id).first()
    if not location_exists:
        logger.warning(f"Location ID {location_id} does not exist.")
        raise HTTPException(status_code=404, detail="Location not found.")
    
    # Create Fact instance using the description from the request body
    new_fact = Fact(description=fact.description, location_id=location_id, user_id=current_user.id)  # Include user_id
    
    try:
        db.add(new_fact)
        db.commit()
        db.refresh(new_fact)  # Refresh the instance to get the new id and created_at
        logger.info(f"Fact created successfully: {new_fact.id} for location ID: {location_id}")
        return FactResponse.model_validate(new_fact)  # Transforming the SQLAlchemy model to Pydantic response model
    except Exception as e:
        logger.error(f"Error creating fact: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the fact.")


@router.delete("/locations/{location_id}/facts/{fact_id}", status_code=204)  # Route for deleting a fact by location
def delete_fact(
    location_id: int, 
    fact_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)  # Ensure user is authenticated
):
    logger.info(f"Attempting to delete fact with ID: {fact_id} for location ID: {location_id} by user ID: {current_user.id}")
    
    # Check if the location ID exists
    location_exists = db.query(Location).filter(Location.id == location_id).first()
    if not location_exists:
        logger.warning(f"Location ID {location_id} does not exist.")
        raise HTTPException(status_code=404, detail="Location not found.")
    
    # Find the fact to delete
    fact_to_delete = db.query(Fact).filter(Fact.id == fact_id, Fact.location_id == location_id).first()
    
    if fact_to_delete is None:
        logger.warning(f"Fact with ID {fact_id} not found for location ID {location_id}.")
        raise HTTPException(status_code=404, detail="Fact not found.")
    
    db.delete(fact_to_delete)
    db.commit()
    
    logger.info(f"Fact with ID {fact_id} deleted successfully for location ID: {location_id}.")


@router.put("/locations/{location_id}/facts/{fact_id}", response_model=FactResponse)  # Route for updating a fact by location
def update_fact(
    location_id: int, 
    fact_id: int, 
    fact: FactCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)  # Ensure user is authenticated
):
    logger.info(f"Updating fact with ID: {fact_id} for location ID: {location_id} with new description: {fact.description} by user ID: {current_user.id}")
    
    # Check if the location ID exists
    location_exists = db.query(Location).filter(Location.id == location_id).first()
    if not location_exists:
        logger.warning(f"Location ID {location_id} does not exist.")
        raise HTTPException(status_code=404, detail="Location not found.")
    
    # Find the fact to update
    fact_to_update = db.query(Fact).filter(Fact.id == fact_id, Fact.location_id == location_id).first()
    
    if fact_to_update is None:
        logger.warning(f"Fact with ID {fact_id} not found for location ID {location_id}.")
        raise HTTPException(status_code=404, detail="Fact not found.")
    
    # Update the fact's attributes
    fact_to_update.description = fact.description

    try:
        db.commit()  # Commit the changes to the database
        logger.info(f"Fact with ID {fact_id} updated successfully for location ID: {location_id}.")
        return FactResponse.model_validate(fact_to_update)  # Return the updated fact
    except IntegrityError:
        logger.warning(f"Failed to update fact with ID: {fact_id}.")
        db.rollback()
        raise HTTPException(status_code=400, detail="An error occurred while updating the fact.")
    except Exception as e:
        logger.error(f"Error updating fact: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the fact.")