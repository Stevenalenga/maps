from pydantic import BaseModel
from datetime import datetime

class FriendshipBase(BaseModel):
    user_id: int

class FriendshipCreate(FriendshipBase):
    friend_id: int

class Friendship(FriendshipBase):
    id: int
    friend_id: int
    created_at: datetime
    
    class Config:
        form_attributes = True