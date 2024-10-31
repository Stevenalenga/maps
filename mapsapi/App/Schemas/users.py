from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
  

class UserBase(BaseModel):
    username: str
    email: EmailStr  # Use EmailStr for email validation

    class Config:
        from_attributes = True  # Allows creating Pydantic models from ORM objects

class UserCreate(UserBase):
    username: str
    email: str
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr  # Use EmailStr for email validation
    password: str

class UserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: Optional[datetime] = None