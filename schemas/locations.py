from pydantic import BaseModel
from datetime import datetime
from schemas.users import User
from typing import List

class LocationBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    description: str  

    class Config:
        arbitrary_types_allowed = True

class LocationCreate(LocationBase):
    tags: List[str]  # Add this line

class Location(LocationBase):
    id: int
    created_at: datetime
    owner: User  

class LocationSchema(LocationBase):
    id: str
    user_id: str
    created_at: datetime
    tags: List[str]  # Add this line

    class Config:
        from_attributes = True
