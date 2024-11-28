# schemas/auth.py
from pydantic import BaseModel,EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str



class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    username: str
    email: EmailStr

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    id: int

    class Config:
        from_attributes = True