import sys
import os
from fastapi import FastAPI
from dotenv import load_dotenv
from mongoengine import connect
from routes.auth import router as auth_router
from routes.users import router as users_router
from database.database import db


# Initialize FastAPI app
app = FastAPI(
    title="My API",
    description="This is a maps api project, meant to give details on locations",
    version="3.5.0",
    terms_of_service="http://mola.com/terms/",
    contact={
        "name": "Steven Alenga",
        "url": "http://steven.alenga@gmail.com/contact/",
        "email": "steven.alenga@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

db()

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users",tags=["users"])
"""
app.include_router(locations.router, tags=["locations"])
app.include_router(tags.router, tags=["tags"])
app.include_router(friendships.router, tags=["friendships"])
app.include_router(facts.router, tags=["facts"])
"""

@app.get("/")
async def root():
    return {"message": "It works!"}


