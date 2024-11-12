from sqlalchemy import Column, Integer, String, ForeignKey, DateTime,Float, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from sqlalchemy.sql import func
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String )
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    locations = relationship("Location", back_populates="owner")
    friendships = relationship("Friendship", back_populates="user", foreign_keys="Friendship.user_id")


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)  # Change to Float
    longitude = Column(Float, nullable=False)  # Change to Float
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    owner = relationship("User", back_populates="locations")
    facts = relationship("Fact", back_populates="location")

    __table_args__ = (
        UniqueConstraint('latitude', 'longitude', name='uq_lat_long'),  # Ensure unique latitude and longitude
    )

class Fact(Base):
    __tablename__ = "facts"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # New field for user ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String, default="user")

    location = relationship("Location", back_populates="facts")
    user = relationship("User")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow) 

    user = relationship("User", back_populates="friendships", foreign_keys=[user_id])
    friend = relationship("User", foreign_keys=[friend_id])
