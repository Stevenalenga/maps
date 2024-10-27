from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from typing import List
from DB.database import SessionLocal
from Models.models import User, Location, Image, Fact
from Schemas.schemas import UserCreate, UserLogin, LocationCreate, ImageCreate, FactCreate, AIQuery, UserSchema,Location, Image,Fact,Token
from Utils.utils import get_password_hash, verify_password
from Oauth.oauth2 import google_oauth, facebook_oauth
from Utils.ai_utils import get_nearby_locations
from Oauth.oauth import get_current_user, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

app = FastAPI()
router = APIRouter(prefix="/mapapi/v1")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes

#oauth
@router.post("/auth/register", response_model=UserSchema)
def register_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Check if user already exists
    if db.query(User).filter(User.email == form_data.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = get_password_hash(form_data.password)
    db_user = User(username=form_data.username, email=form_data.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserSchema.model_validate(db_user)  # Use from_orm to convert to Pydantic schema

@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)  # Token expiration time
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

#Oauth2
@router.post("/auth/login/google")
async def login_google(code: str):
    """Endpoint for Google login"""
    user_info = await google_oauth(code)
    return {"message": "Successfully logged in with Google", "user_info": user_info}

@router.post("/auth/login/facebook")
async def login_facebook(access_token: str):
    """Endpoint for Facebook login"""
    user_info = await facebook_oauth(access_token)
    return {"message": "Successfully logged in with Facebook", "user_info": user_info}


#locations

@router.post("/locations", response_model=Location)
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    print("hwo")
    db_location = Location(**location.model_dump())  # Adjusted to use dict()
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


@router.get("/locations", response_model=List[Location])
def search_locations(query: str, db: Session = Depends(get_db)):
    locations = db.query(Location).filter(Location.name.contains(query)).all()
    return locations

@router.get("/locations/nearby")
async def get_locations(user_lat: float, user_long: float, radius: float):
    user_location = (user_lat, user_long)
    locations = get_nearby_locations(user_location, radius)
    return {"nearby_locations": locations}

@router.post("/locations/{location_id}/share")
def share_location(location_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    location = db.query(Location).get(location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    # Implement sharing logic, possibly returning a shareable link or reference
    return {"message": "Location shared successfully"}

@router.post("/locations/{location_id}/images", response_model=Image)
def add_image(location_id: int, image: ImageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    location = db.query(Location).get(location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    
    db_image = Image(**image.model_dump(), location_id=location.id)  # Use .dict() for Pydantic models
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@router.post("/locations/{location_id}/facts", response_model=Fact)
def add_fact(location_id: int, fact: FactCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    location = db.query(Location).get(location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    
    db_fact = Fact(**fact.model_dump(), location_id=location.id)  
    db.add(db_fact)
    db.commit()
    db.refresh(db_fact)
    return db_fact

#aiquery
@router.post("/ai-query")
def ai_query(query: AIQuery, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Endpoint to get nearby locations based on AI query.
    
    :param query: AIQuery object containing latitude, longitude, and radius.
    :param db: Database session dependency.
    :return: List of nearby locations within the specified radius.
    """
    user_location = {
        "latitude": query.latitude,
        "longitude": query.longitude
    }
    results = get_nearby_locations(user_location, query.radius)
    return results

app.include_router(router)
