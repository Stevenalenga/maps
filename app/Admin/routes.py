# ... existing imports ...
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import mapsapi.App.Schemas.schemas as schemas, crud
from database import get_db

router = APIRouter()

# Existing create_user and read_user functions
@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db=db, user=user)
    return db_user

@router.get("/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/", response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db)):
    users = crud.get_users(db)
    return users


@router.put("/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db=db, user_id=user_id, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    result = crud.delete_user(db=db, user_id=user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}

# ... existing code ...


@router.put("/{user_id}", response_model=Userschema)  # {{ edit_1 }} Define the update route
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db),):
    logger.info(f"Updating user with ID: {user_id}")
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