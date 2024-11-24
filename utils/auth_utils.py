from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt, ExpiredSignatureError
from models.models import User
from schemas.auth import TokenData
import os
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v3/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
 
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience="fastapi-users")
        username: str = payload.get("sub")
        if not username or not isinstance(username, str):
            logger.error("Invalid or missing 'sub' claim in token")
            raise credentials_exception
        token_data = TokenData(username=username)
    except ExpiredSignatureError as e:
        logger.error(f"Expired token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError as e:
        logger.error(f"JWT error: {e}")
        raise credentials_exception

    # Retrieve the user from the database
    try:
        user = User.objects(username=token_data.username).first()
        if user is None:
            logger.warning(f"User not found for username: {token_data.username}")
            raise credentials_exception
        logger.info(f"Authenticated user: {user.id}")
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    logger.info(f"User {token_data.username} successfully authenticated")
    return user
