from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from Auth import auth
from Api import users ,locations


# Initialize the FastAPI application
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables
@app.on_event("startup")  # Use on_event for startup
async def startup():
  Base.metadata.create_all(bind=engine)

  yield  

# Include the routers for different API endpoints
app.include_router(auth.router)
app.include_router(users.router, tags=["users"])
app.include_router(locations.router, tags=["locations"])
#app.include_router(tags.router, prefix="/tags", tags=["tags"])
#app.include_router(friendships.router, prefix="/friendships", tags=["friendships"])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the My FastAPI App API!"}
