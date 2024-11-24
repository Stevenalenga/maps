from pydantic import BaseModel
from datetime import datetime

class FactBase(BaseModel):
    description: str
   
    


class Fact(FactBase):
    id: int
    created_at: datetime  
      

    class Config:
        from_attributes= True  

class FactCreate(FactBase):
    class Config:
        from_attributes= True 



class FactResponse(BaseModel):
    id: str
    description: str
    location_id: str
    user_id : str
    created_at: datetime
    

    class Config:
        from_attributes = True



