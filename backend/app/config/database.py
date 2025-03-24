from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "resume_analyzer")

# Create synchronous client for use in initialization scripts
client = MongoClient(MONGO_URL)
db = client[DB_NAME]

# Create async client for use in FastAPI app
async_client = AsyncIOMotorClient(MONGO_URL)
async_db = async_client[DB_NAME]

# Collection references
resume_collection = db["resumes"]
job_collection = db["jobs"]
match_collection = db["matches"]

# Async collection references
async_resume_collection = async_db["resumes"]
async_job_collection = async_db["jobs"]
async_match_collection = async_db["matches"]

# Initialize database with indexes
def init_db():
    # Create text indexes for search
    resume_collection.create_index([("candidate_name", "text"), ("skills.name", "text")])
    job_collection.create_index([("title", "text"), ("company_name", "text"), ("required_skills.name", "text")])
    
    # Create indexes for faster lookups
    resume_collection.create_index("created_at")
    job_collection.create_index("created_at")
    match_collection.create_index([("resume_id", 1), ("job_id", 1)], unique=True)
    match_collection.create_index("match_score")

# Close connections when app shuts down
def close_mongo_connection():
    client.close()
    async_client.close() 