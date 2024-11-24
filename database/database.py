
import sys
import os
from dotenv import load_dotenv
from mongoengine import connect



# Load environment variables
load_dotenv()

# Add the current directory to the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# MongoDB Connection
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
PORT = int(os.getenv("PORT"))

if not MONGO_URI or not MONGO_URI.startswith(("mongodb://", "mongodb+srv://")):
    raise ValueError("Invalid MongoDB URI. It must begin with 'mongodb://' or 'mongodb+srv://'")

def db ():
    
    connect(db=DATABASE_NAME, host=MONGO_URI, port=PORT)
