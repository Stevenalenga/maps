from pydantic import BaseModel
from datetime import datetime
from Schemas.users import User

class LocationBase(BaseModel):
    name: str
    latitude: str
    longitude: str

    class Config:
        arbitrary_types_allowed = True


class LocationCreate(LocationBase):
    pass


class Location(LocationBase):
    id: int
    created_at: datetime
    owner: User  


class LocationSchema(LocationBase):
    id: int
    user_id: int  
    created_at: datetime

    class Config:
        orm_mode = True  

  