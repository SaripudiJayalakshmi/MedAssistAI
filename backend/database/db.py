# db.py
# Sets up the connection to our MongoDB Atlas database.

import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI")

client = MongoClient(MONGO_URI)          # connects to your Atlas cluster
db = client["medassist_ai"]              # the actual database (created automatically on first write)

# Collections (like tables) we'll use
users_collection = db["users"]