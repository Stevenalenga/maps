from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Schemas.friendships import FriendshipCreate, Friendship
from models import Friendship as FriendshipModel
from database import get_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2")

@router.post("/friendships", response_model=Friendship)
def create_friendship(friendship: FriendshipCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating friendship between user {friendship.user_id} and {friendship.friend_id}")
    
    # Check if the friendship already exists
    existing_friendship = db.query(FriendshipModel).filter(
        FriendshipModel.user_id == friendship.user_id,
        FriendshipModel.friend_id == friendship.friend_id
    ).first()
    
    if existing_friendship:
        logger.warning(f"Friendship already exists between user {friendship.user_id} and {friendship.friend_id}")
        raise HTTPException(status_code=400, detail="Friendship already exists.")

    # Create a new friendship
    db_friendship = FriendshipModel(user_id=friendship.user_id, friend_id=friendship.friend_id)
    
    db.add(db_friendship)
    db.commit()
    db.refresh(db_friendship)
    
    logger.info(f"Friendship created successfully: {db_friendship.id}")
    return db_friendship

@router.delete("/friendships/{friendship_id}", status_code=204)  # New route for deleting a friendship
def delete_friendship(friendship_id: int, db: Session = Depends(get_db)):
    logger.info(f"Attempting to delete friendship with ID: {friendship_id}")
    
    # Find the friendship to delete
    friendship_to_delete = db.query(FriendshipModel).filter(FriendshipModel.id == friendship_id).first()
    
    if friendship_to_delete is None:
        logger.warning(f"Friendship with ID {friendship_id} not found.")
        raise HTTPException(status_code=404, detail="Friendship not found.")
    
    db.delete(friendship_to_delete)
    db.commit()
    
    logger.info(f"Friendship with ID {friendship_id} deleted successfully.")


@router.get("/users/{user_id}/friendship-count", response_model=int)  # New route for counting friendships
def get_friendship_count(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Getting friendship count for user ID: {user_id}")
    
    # Count the number of friendships for the user
    friendship_count = db.query(FriendshipModel).filter(
        (FriendshipModel.user_id == user_id) | (FriendshipModel.friend_id == user_id)
    ).count()
    
    logger.info(f"User ID {user_id} has {friendship_count} friendships.")
    return friendship_count
