from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.Auth import auth
from app.Api import users, locations, tags, friendships, facts
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

# Initialize the FastAPI application
app = FastAPI(
    title="My API",
    description="This is a maps api project, meant to give details on locations",
    version="3.5.0",
    terms_of_service="https://github.com/Stevenalenga/maps/blob/main/README.md",
    contact={
        "name": "Steven Alenga",
        "url": "https://portfolio-x9a4.vercel.app/",
        "email": "steven.alenga@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Perform any cleanup here if necessary

app.router.lifespan_context = lifespan

# Include the routers for different API endpoints
app.include_router(auth.router)
app.include_router(users.router, tags=["users"])
app.include_router(locations.router, tags=["locations"])
app.include_router(tags.router, tags=["tags"])
app.include_router(friendships.router, tags=["friendships"])
app.include_router(facts.router, tags=["facts"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the My FastAPI App API!"}
