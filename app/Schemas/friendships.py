from pydantic import BaseModel
from datetime import datetime


class FriendshipBase(BaseModel):
    
    user_id: int

class FriendshipCreate(BaseModel):
    
    friend_id: int

class Friendship(FriendshipBase):
    
    id: int
    friend_id: int
    created_at: datetime

    class Config:
        from_attributes = True 


