from fastapi import FastAPI
from DB.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from Routes import routes,auth


# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="My API",
    description="This is a maps api project, meant to give details on locations",
    version="2.5.0",
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify allowed origins, or use ["http://localhost:3000"] for local development
    allow_credentials=True,
    allow_methods=["*"],  # Specify methods (GET, POST, etc.) if needed
    allow_headers=["*"],  # Specify headers if needed
)

# Initialize the database
Base.metadata.create_all(bind=engine)

# Include the routes
app.include_router(auth.router)
app.include_router(routes.router, prefix="/api")






@app.get("/")
async def root():
    return {"message": "Welcome to the Maps API"}

# Optional: You can add middleware, exception handling, or logging here


