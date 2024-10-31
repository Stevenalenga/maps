from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


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
