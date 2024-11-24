from fastapi import APIRouter, Depends, HTTPException
from mongoengine import DoesNotExist, NotUniqueError
from typing import List
import logging
from bson import ObjectId  # Import ObjectId
from models.models import Friendship, User
from schemas.friendships import FriendshipResponse, FriendshipCreate
from utils.auth_utils import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3")

@router.post("/friendships/{friend_id}", response_model=FriendshipResponse)
def create_friendship(friend_id: str, current_user=Depends(get_current_user)):
    logger.info(f"Creating friendship for user: {current_user.id} with friend: {friend_id}")
    
    # Ensure the friend_id exists
    try:
        friend = User.objects.get(id=friend_id)
    except DoesNotExist:
        logger.warning(f"Friend with ID {friend_id} does not exist.")
        raise HTTPException(status_code=404, detail="Friend not found.")
    
    # Check if the friendship already exists
    if Friendship.objects(user_id=current_user.id, friend_id=friend_id).first():
        logger.warning(f"Friendship already exists between user {current_user.id} and friend {friend_id}.")
        raise HTTPException(status_code=400, detail="Friendship already exists.")
    
    db_friendship = Friendship(user_id=current_user.id, friend_id=friend_id)
    try:
        db_friendship.save()
        logger.info(f"Friendship created successfully: {db_friendship.id}")
        return FriendshipResponse(
            id=str(db_friendship.id),
            user_id=str(db_friendship.user_id.id),
            friend_id=str(db_friendship.friend_id.id),
            created_at=db_friendship.created_at
        )
    except Exception as e:
        logger.error(f"Error creating friendship: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the friendship.")

@router.get("/friendships", response_model=List[FriendshipResponse])
def get_friendships(current_user=Depends(get_current_user)):
    logger.info(f"Fetching friendships for user: {current_user.id}")
    friendships = Friendship.objects(user_id=current_user.id)
    logger.info(f"Found {len(friendships)} friendships")
    return [FriendshipResponse(
        id=str(friendship.id),
        user_id=str(friendship.user_id.id),
        friend_id=str(friendship.friend_id.id),
        created_at=friendship.created_at
    ) for friendship in friendships]

@router.delete("/friendships/{friendship_id}", status_code=204)
def delete_friendship(friendship_id: str, current_user=Depends(get_current_user)):
    logger.info(f"Attempting to delete friendship with ID: {friendship_id}")
    try:
        friendship_to_delete = Friendship.objects.get(id=ObjectId(friendship_id), user_id=current_user.id)  # Convert to ObjectId
        friendship_to_delete.delete()
        logger.info(f"Friendship with ID {friendship_id} deleted successfully.")
    except DoesNotExist:
        logger.warning(f"Friendship with ID {friendship_id} not found.")
        raise HTTPException(status_code=404, detail="Friendship not found.")
    return {"detail": "Friendship deleted successfully"}