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
    id: int
    description: str
    location_id: int
    user_id : int
    created_at: datetime
    

    class Config:
        from_attributes = True  



