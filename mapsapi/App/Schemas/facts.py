from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


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