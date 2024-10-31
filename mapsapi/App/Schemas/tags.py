from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime




class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class Tag(TagBase):
    id: int

    class Config:
        from_attributes = True