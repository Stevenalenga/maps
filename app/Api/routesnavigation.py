from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import Route as Routemodels, User as Usermodels
from ..Schemas.routesnavigation import Route 
from Utils.oauth2 import get_current_user

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/routes")

@router.post("/create", response_model=Route)
def save_route(route: Route, db: Session = Depends(get_db), current_user: Usermodels = Depends(get_current_user)):
    logger.info(f"Saving route with ID: {route.route_id}")
    try:
        db_route = Routemodels(
            route_id=route.route_id,
            from_=route.from_,
            to=route.to,
            waypoints=str(route.waypoints),  # Convert list to string for storage
            distance=route.distance,
            estimated_time=route.estimated_time,
            mode=route.mode,
            user_id=current_user.id
        )
        db.add(db_route)
        db.commit()
        db.refresh(db_route)
        logger.info(f"Route saved successfully: {route.route_id}")
        return db_route
    except Exception as e:
        logger.error(f"Error saving route {route.route_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while saving the route")

@router.get("/{route_id}", response_model=Route)
def get_route(route_id: int, db: Session = Depends(get_db), current_user: Usermodels = Depends(get_current_user)):
    logger.info(f"Fetching route with ID: {route_id}")
    db_route = db.query(Routemodels).filter(Routemodels.route_id == route_id, Routemodels.user_id == current_user.id).first()
    if db_route is None:
        logger.error(f"Route not found: {route_id}")
        raise HTTPException(status_code=404, detail="Route not found")
    return db_route

@router.put("/{route_id}", response_model=Route)
def update_route(route_id: int, route: Route, db: Session = Depends(get_db), current_user: Usermodels = Depends(get_current_user)):
    logger.info(f"Updating route with ID: {route_id}")
    db_route = db.query(Routemodels).filter(Routemodels.route_id == route_id, Routemodels.user_id == current_user.id).first()
    if db_route is None:
        logger.error(f"Route not found: {route_id}")
        raise HTTPException(status_code=404, detail="Route not found")
    try:
        db_route.from_ = route.from_
        db_route.to = route.to
        db_route.waypoints = str(route.waypoints)  # Convert list to string for storage
        db_route.distance = route.distance
        db_route.estimated_time = route.estimated_time
        db_route.mode = route.mode
        db.commit()
        db.refresh(db_route)
        logger.info(f"Route updated successfully: {route_id}")
        return db_route
    except Exception as e:
        logger.error(f"Error updating route {route_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error updating route")

@router.delete("/{route_id}", response_model=Route)
def delete_route(route_id: int, db: Session = Depends(get_db), current_user: Usermodels = Depends(get_current_user)):
    logger.info(f"Deleting route with ID: {route_id}")
    db_route = db.query(Routemodels).filter(Routemodels.route_id == route_id, Routemodels.user_id == current_user.id).first()
    if db_route is None:
        logger.error(f"Route not found: {route_id}")
        raise HTTPException(status_code=404, detail="Route not found")
    try:
        db.delete(db_route)
        db.commit()
        logger.info(f"Route deleted successfully: {route_id}")
        return db_route
    except Exception as e:
        logger.error(f"Error deleting route {route_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error deleting route")
