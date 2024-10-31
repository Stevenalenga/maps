from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from Schemas.users import User as Userschema
from models import User as Usermodels
from database import get_db

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

