from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.Schemas.users import User as Userschema, UserUpdate
from app.models import User as Usermodels
from app.database import get_db
from app.Auth.auth import get_password_hash
from app.Utils.oauth2 import get_current_user


import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/users")


@router.get("/{user_id}", response_model=Userschema)
def read_user(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching user with ID: {user_id}")
    try:
        db_user = db.query(Usermodels).filter(Usermodels.id == user_id).first()
        if db_user is None:
            logger.warning(f"User not found: user_id={user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"User retrieved successfully: {db_user.username} with email: {db_user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the user")

@router.put("/{user_id}", response_model=Userschema)  
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: Usermodels = Depends(get_current_user)  # Ensure the current user is fetched
):
    logger.info(f"Updating user with ID: {user_id}")
    
    # Check if the current user is trying to update their own information
    if current_user.id != user_id:
        logger.warning(f"Unauthorized update attempt by user {current_user.id} for user_id={user_id}")
        raise HTTPException(status_code=403, detail="You are not allowed to update this user")

    try:
        db_user = db.query(Usermodels).filter(Usermodels.id == user_id).first()
        if db_user is None:
            logger.warning(f"User not found: user_id={user_id}")
            raise HTTPException(status_code=404, detail="User not found")

        # Update user fields
        db_user.username = user_update.username
        db_user.email = user_update.email
        db_user.password = get_password_hash(user_update.password)  # Assuming you have a function to hash passwords

        db.commit()  # Commit the changes to the database
        db.refresh(db_user)  # Refresh the instance to get updated values
        logger.info(f"User updated successfully: {db_user.username} with email: {db_user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the user")
