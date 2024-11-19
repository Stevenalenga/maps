from pydantic import BaseModel
from typing import List, Dict

class RouteBase(BaseModel):
    route_id: str
    from_: Dict[str, Dict[str, float]]
    to: Dict[str, Dict[str, float]]
    waypoints: List[Dict[str, float]]
    distance: str
    estimated_time: str
    mode: str

class RouteCreate(RouteBase):
    pass

class Route(RouteBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True
