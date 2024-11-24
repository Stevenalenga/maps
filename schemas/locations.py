from pydantic import BaseModel
from datetime import datetime
from schemas.users import User

class LocationBase(BaseModel):
    name: str
    latitude: float
    longitude: float
    description: str  # New property

    class Config:
        arbitrary_types_allowed = True

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    created_at: datetime
    owner: User  

class LocationSchema(LocationBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

