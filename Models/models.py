from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from DB.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Change this line to match the back_populates in Location
    locations = relationship("Location", back_populates="owner")

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Add this line to complete the relationship
    owner = relationship("User", back_populates="locations")
    images = relationship("Image", back_populates="location", cascade="all, delete-orphan")
    facts = relationship("Fact", back_populates="location", cascade="all, delete-orphan")

class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    image_url = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"))

    location = relationship("Location", back_populates="images")

class Fact(Base):
    __tablename__ = "facts"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"))

    location = relationship("Location", back_populates="facts")
