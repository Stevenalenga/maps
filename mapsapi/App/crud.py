from sqlalchemy.orm import Session
import models, schemas

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_location(db: Session, location: schemas.LocationCreate, user_id: int):
    db_location = models.Location(**location.dict(), user_id=user_id)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def get_locations(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Location).offset(skip).limit(limit).all()

def create_fact(db: Session, fact: schemas.FactCreate):
    db_fact = models.Fact(**fact.dict())
    db.add(db_fact)
    db.commit()
    db.refresh(db_fact)
    return db_fact

def get_facts_by_location(db: Session, location_id: int):
    return db.query(models.Fact).filter(models.Fact.location_id == location_id).all()
