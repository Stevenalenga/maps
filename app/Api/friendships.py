from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Schemas.friendships import Friendship  # Pydantic models
from models import Friendship as FriendshipModel, User  # SQLAlchemy models
from database import get_db
from Utils.oauth2 import get_current_user
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2")

@router.post("/friendships/{friend_id}", response_model=Friendship)  # Use Pydantic model as response
def create_friendship(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # Ensure user is logged in
):
    logger.info(f"Creating friendship between user {current_user.id} and {friend_id}")

    # Check if the user to befriend exists
    friend_to_befriend = db.query(User).filter(User.id == friend_id).first()
    if not friend_to_befriend:
        logger.warning(f"User to befriend with ID {friend_id} does not exist.")
        raise HTTPException(status_code=404, detail="User to befriend does not exist.")

    # Check if the friendship already exists
    existing_friendship = db.query(FriendshipModel).filter(
        FriendshipModel.user_id == current_user.id,
        FriendshipModel.friend_id == friend_id
    ).first()
    
    if existing_friendship:
        logger.warning(f"Friendship already exists between user {current_user.id} and {friend_id}")
        raise HTTPException(status_code=400, detail="Friendship already exists.")

    # Create a new friendship
    db_friendship = FriendshipModel(user_id=current_user.id, friend_id=friend_id)
    
    db.add(db_friendship)
    db.commit()
    db.refresh(db_friendship)
    
    logger.info(f"Friendship created successfully between user {current_user.id} and {friend_id}")
    # Return the new friendship as a Pydantic model
    return Friendship(
        id=db_friendship.id,
        user_id=db_friendship.user_id,
        friend_id=db_friendship.friend_id,
        created_at=db_friendship.created_at
    )

@router.delete("/friendships/{friendship_id}", status_code=204)  # Route for deleting a friendship
def delete_friendship(
    friendship_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)  # Ensure user is logged in
):
    logger.info(f"Attempting to delete friendship with ID: {friendship_id} for user {current_user.id}")
    
    # Find the friendship to delete
    friendship_to_delete = db.query(FriendshipModel).filter(
        FriendshipModel.id == friendship_id,
        FriendshipModel.user_id == current_user.id  # Ensure the current user is the owner of the friendship
    ).first()
    
    if not friendship_to_delete:  # More Pythonic way to check for None
        logger.warning(f"Friendship with ID {friendship_id} not found or does not belong to user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Friendship not found or does not belong to the user.")
    
    db.delete(friendship_to_delete)
    db.commit()
    
    logger.info(f"Friendship with ID {friendship_id} deleted successfully for user {current_user.id}.")
    

class FriendshipCountResponse(BaseModel):
    count: int

@router.get("/users/{user_id}/friendship-count", response_model=FriendshipCountResponse)  # Return count in Pydantic model
def get_friendship_count(
    user_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)  # Ensure user is logged in
):
    logger.info(f"Getting friendship count for user ID: {user_id} by user ID: {current_user.id}")
    
    # Check if the user exists
    user_to_check = db.query(User).filter(User.id == user_id).first()
    if user_to_check is None:
        logger.warning(f"User with ID {user_id} does not exist.")
        raise HTTPException(status_code=404, detail="User not found.")

    # Count the number of friendships for the user
    friendship_count = db.query(FriendshipModel).filter(
        (FriendshipModel.user_id == user_id) | (FriendshipModel.friend_id == user_id)
    ).count()
    
    logger.info(f"User ID {user_id} has {friendship_count} friendships.")
    return FriendshipCountResponse(count=friendship_count)  # Return count in response model