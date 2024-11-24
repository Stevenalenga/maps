from pydantic import BaseModel
from datetime import datetime

class FriendshipBase(BaseModel):
    user_id: int

class FriendshipCreate(FriendshipBase):  # Inherit from FriendshipBase
    friend_id: int

class Friendship(FriendshipBase):
    id: int
    friend_id: int
    created_at: datetime

    class Config:
        from_attributes = True 

class FriendshipResponse(BaseModel):
    id: str
    user_id: str
    friend_id: str
    created_at: datetime


