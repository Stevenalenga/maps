from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from sqlalchemy.orm import Session
from typing import List
from DB.database import SessionLocal
from Models.models import User, Location as LocationModel, Image, Fact
from Schemas.schemas import UserCreate, UserLogin, LocationCreate, ImageCreate, FactCreate, AIQuery, UserSchema, LocationSchema, Image, Fact, Token
from Utils.utils import get_password_hash, verify_password
from Oauth.oauth import google_oauth, facebook_oauth
from Utils.ai_utils import get_nearby_locations
from Oauth.oauth2 import get_current_user, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security, Request
from decouple import config
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
import logging
from fastapi import FastAPI, Depends, HTTPException, APIRouter, status, Request
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import JSONResponse
from logging.handlers import RotatingFileHandler
from starlette.status import HTTP_403_FORBIDDEN
import traceback
from sqlalchemy.exc import SQLAlchemyError

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure FastAPI's logger uses the correct logging level
gunicorn_logger = logging.getLogger("gunicorn.error")
fastapi_logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    fastapi_logger.setLevel(gunicorn_logger.level)
else:
    fastapi_logger.setLevel(logging.INFO)

API_KEY = config("APP_API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_api_key(request: Request, api_key_header: str = Security(api_key_header)):
    if request.url.path.startswith("/api/mapapi/v1/auth"):
        return True  # Allow access to all auth routes without API key
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate API Key"
    )

app = FastAPI()
router = APIRouter(prefix="/mapapi/v1", dependencies=[Depends(get_api_key)])

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
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to register user: {user.username}")
    try:
        # Check if username or email already exists
        db_user = db.query(User).filter(
            (User.username == user.username) | (User.email == user.email)
        ).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Username or email already registered")
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"User registered successfully: {user.username}")
        return db_user
    except HTTPException as e:
        logger.error(f"Registration failed for user {user.username}: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration for user {user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

"""@router.post("/auth/login", response_model=Token, dependencies=[])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {form_data.username}")
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
    logger.info(f"User logged in successfully: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}
"""
#Oauth2
@router.post("/auth/login/google", dependencies=[])
async def login_google(code: str):
    """Endpoint for Google login"""
    user_info = await google_oauth(code)
    return {"message": "Successfully logged in with Google", "user_info": user_info}

@router.post("/auth/login/facebook", dependencies=[])
async def login_facebook(access_token: str):
    """Endpoint for Facebook login"""
    user_info = await facebook_oauth(access_token)
    return {"message": "Successfully logged in with Facebook", "user_info": user_info}

# Add this near your other imports
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Add this to your existing in-memory storage or database
blacklisted_tokens = set()

@router.post("/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    logger.info("User logout attempt")
    try:
        blacklisted_tokens.add(token)
        logger.info("User successfully logged out")
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed")

# Modify your get_current_user function to check for blacklisted tokens

#locations

@router.get("/locations", response_model=List[LocationSchema])
async def get_user_locations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Fetching locations for user: {current_user.id}")
        user_locations = db.query(LocationModel).filter(LocationModel.user_id == current_user.id).all()
        logger.info(f"Retrieved {len(user_locations)} locations for user: {current_user.id}")
        return user_locations
    except Exception as e:
        logger.error(f"Error fetching locations for user {current_user.id}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="An error occurred while fetching locations")

@router.post("/locations", response_model=LocationSchema)
async def create_location(
    location: LocationCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    try:
        logger.info(f"Creating new location for user: {current_user.id}")
        location_data = location.model_dump()
        db_location = LocationModel(**location_data, user_id=current_user.id)
        db.add(db_location)
        db.commit()
        db.refresh(db_location)
        logger.info(f"Location created successfully for user: {current_user.id}")
        return db_location
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error creating location for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the location")
    except Exception as e:
        logger.error(f"Unexpected error creating location for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/locations/nearby")
async def get_locations(user_lat: float, user_long: float, radius: float):
    user_location = (user_lat, user_long)
    locations = get_nearby_locations(user_location, radius)
    return {"nearby_locations": locations}

@router.post("/locations/{location_id}/share")
def share_location(location_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    location = db.query(LocationModel).get(location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    # Implement sharing logic, possibly returning a shareable link or reference
    return {"message": "Location shared successfully"}

@router.post("/locations/{location_id}/images", response_model=Image)
def add_image(location_id: int, image: ImageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    location = db.query(LocationModel).get(location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    
    db_image = Image(**image.model_dump(), location_id=location.id)  # Use .dict() for Pydantic models
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image

@router.post("/locations/{location_id}/facts", response_model=Fact)
def add_fact(location_id: int, fact: FactCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    location = db.query(LocationModel).get(location_id)
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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred."},
    )

# Set up file handler
file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

# Add file handler to the logger
logger.addHandler(file_handler)
