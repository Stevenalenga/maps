from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import logging
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from schemas.auth import UserCreate, UserResponse, UserLogin, Token
from models.models import User
from mongoengine.queryset.visitor import Q
from dotenv import load_dotenv
import os
from fastapi import Form

# Load environment variables
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI Router
router = APIRouter(prefix="/api/v3")
logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v3/login")

# Utility Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "aud": "fastapi-users"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    logger.info(f"Signup request received: {user.username}")
    try:
        existing_user = User.objects(username=user.username).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        
        existing_email = User.objects(email=user.email).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
        
        hashed_password = get_password_hash(user.password)
        new_user = User(username=user.username, email=user.email, password=hashed_password)
        new_user.save()
        logger.info(f"User created successfully: {user.username}")
        return UserResponse(username=new_user.username, email=new_user.email)
    except Exception as e:
        logger.error(f"Unexpected error during signup: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/login", response_model=Token)
async def login(username: str = Form(...), password: str = Form(...)):
    logger.info(f"Login attempt for user: {username}")
    try:
        db_user = User.objects(Q(username=username) | Q(email=username)).first()
        if not db_user or not verify_password(password, db_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": db_user.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Unexpected error during login: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")