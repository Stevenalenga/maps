from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

# User Base Schema
class UserBase(BaseModel):
    username: str
    email: EmailStr  # Use EmailStr for email validation

    class Config:
        from_attributes = True  # Allows creating Pydantic models from ORM objects

# User Creation Schema
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# User Login Schema
class UserLogin(BaseModel):
    email: EmailStr  # Use EmailStr for email validation
    password: str

# User Schema for responses
class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: Optional[datetime] = None  # Make it optional

    class Config:
        from_attributes = True

# Location Base Schema
class LocationBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    description: str | None = None

    class Config:
        from_attributes = True  # Use from_attributes for ORM objects

# Location Creation Schema
class LocationCreate(LocationBase):
    pass

# Location Response Schema
class LocationSchema(LocationBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Image Base Schema
class ImageBase(BaseModel):
    image_url: str  # Renamed for clarity

    class Config:
        from_attributes = True  # Use from_attributes for ORM objects

# Image Creation Schema
class ImageCreate(ImageBase):
    pass

# Image Response Schema
class Image(ImageBase):
    id: int
    location_id: int

# Fact Base Schema
class FactBase(BaseModel):
    description: str

    class Config:
        from_attributes = True  # Use from_attributes for ORM objects

# Fact Creation Schema
class FactCreate(FactBase):
    pass

# Fact Response Schema
class Fact(FactBase):
    id: int
    location_id: int

# AI Query Schema
class AIQuery(BaseModel):
    latitude: float
    longitude: float
    radius: float

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True

