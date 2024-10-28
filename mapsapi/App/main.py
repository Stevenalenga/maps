from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from Api import users, locations, tags, friendships


# Initialize the FastAPI application
app = FastAPI(title="My FastAPI App")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables
@app.on_event("startup")
async def startup():
    # Create all tables
    Base.metadata.create_all(bind=engine)

# Include the routers for different API endpoints
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(locations.router, prefix="/locations", tags=["locations"])
app.include_router(tags.router, prefix="/tags", tags=["tags"])
app.include_router(friendships.router, prefix="/friendships", tags=["friendships"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the My FastAPI App API!"}
