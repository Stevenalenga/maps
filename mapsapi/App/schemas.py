from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
  

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class LocationBase(BaseModel):
    name: str
    latitude: str
    longitude: str

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    created_at: datetime
    owner: User

    class Config:
        from_attributes = True

class FactBase(BaseModel):
    description: str
    location_id: int

class FactCreate(FactBase):
    pass

class Fact(FactBase):
    id: int
    created_at: datetime
    source: str

    class Config:
        from_attributes = True

class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True

class FriendshipBase(BaseModel):
    user_id: int
    friend_id: int

class FriendshipCreate(FriendshipBase):
    pass

class Friendship(FriendshipBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

