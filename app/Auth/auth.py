from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm,OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.Utils.oauth2 import create_access_token,get_password_hash
from Schemas.users import UserSchema,UserCreate
from datetime import timedelta
from passlib.context import CryptContext
import os
from pydantic import EmailStr, BaseModel
import logging
from logging.handlers import RotatingFileHandler
from fastapi.logger import logger as fastapi_logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure FastAPI's logger uses the correct logging level
gunicorn_logger = logging.getLogger("gunicorn.error")
fastapi_logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    fastapi_logger.setLevel(gunicorn_logger.level)
else:
    fastapi_logger.setLevel(logging.INFO)

# Add this import or define the variable here
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

router = APIRouter(prefix="/api/v2", tags=["Authentication"])

class LoginForm(BaseModel):
    username: EmailStr  # Use EmailStr for validation
    password: str

@router.post("/auth/login", summary="Create access token for user")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Validate email format using Pydantic
    try:
        login_data = LoginForm(username=form_data.username, password=form_data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Now db is a valid Session object
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    logger.info(f"User {login_data.username} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}


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
        db_user = User(username=user.username, email=user.email, password=hashed_password)
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v2/auth/login")


blacklisted_tokens = set()

@router.post("/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    logger.info("User logout attempt")
    logger.info(f"Received token: {token}")  # Log the received token
    try:
        if token not in blacklisted_tokens:
            blacklisted_tokens.add(token)
            logger.info("User successfully logged out")
            return {"message": "Successfully logged out"}
        else:
            logger.warning("Token already blacklisted")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token already blacklisted")
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed")


file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=3)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)

# Add file handler to the logger
logger.addHandler(file_handler)