from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.locations import router as locations_router
from routes.tags import router as tags_router
from routes.friendships import router as friendships_router
from routes.facts import router as facts_router
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

# Allow CORS and remote connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

db()

# Include routers
app.include_router(auth_router, tags=["Authentication"])
app.include_router(users_router, prefix="/users",tags=["users"])

app.include_router(locations_router, prefix="/locations", tags=["locations"])
app.include_router(tags_router, prefix="/tags", tags=["tags"])
app.include_router(friendships_router, prefix="/friendships",tags=["friendships"])
app.include_router(facts_router, prefix="/facts", tags=["facts"])

@app.get("/")
async def root():
    return {"Welcome to our maps api project": "This is a project meant to give details on locations"}

@app.get("/status")
async def status():
    return {"status": "API is running"}


