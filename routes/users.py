# routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
import logging
from passlib.context import CryptContext
from schemas.users import UserUpdate, UserResponse
from models import User
from mongoengine import DoesNotExist

# FastAPI Router
router = APIRouter(prefix="/api/v3")
logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Utility Functions
def get_password_hash(password):
    return pwd_context.hash(password)

@router.put("/update/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user_update: UserUpdate):
    logger.info(f"Update request received for user_id: {user_id} with data: {user_update}")
    try:
        db_user = User.objects(id=user_id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Update user fields
        db_user.username = user_update.username
        db_user.email = user_update.email
        db_user.password = get_password_hash(user_update.password)  # Assuming you have a function to hash passwords

        db_user.save()  # Save the changes to the database
        logger.info(f"User updated successfully: {db_user.username} with email: {db_user.email}")
        return UserResponse(username=db_user.username, email=db_user.email)
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the user")

@router.delete("/delete/{user_id}", response_model=UserResponse)
async def delete_user(user_id: str):
    logger.info(f"Delete request received for user_id: {user_id}")
    try:
        db_user = User.objects(id=user_id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        db_user.delete()  # Delete the user from the database
        logger.info(f"User deleted successfully: {db_user.username} with email: {db_user.email}")
        return UserResponse(username=db_user.username, email=db_user.email)
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while deleting the user")
    
@router.get("/get/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    logger.info(f"Get request received for user_id: {user_id}")
    try:
        db_user = User.objects(id=user_id).first()
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        logger.info(f"User retrieved successfully: {db_user.username} with email: {db_user.email}")
        return UserResponse(username=db_user.username, email=db_user.email)
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the user")