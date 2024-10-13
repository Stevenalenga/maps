from fastapi import FastAPI
from DB.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from Routes import routes

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


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
app.include_router(routes.router, prefix="/api", tags=["Maps API"])



@app.get("/")
async def root():
    return {"message": "Welcome to the Maps API"}

# Optional: You can add middleware, exception handling, or logging here
