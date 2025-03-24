from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import motor.motor_asyncio
from beanie import init_beanie

from app.core.config import settings
from app.models.resume import Resume
from app.models.job import JobDescription
from app.models.analysis import ResumeJobMatch
from app.api.routes import resume_router, job_router, analysis_router

# Create FastAPI app
app = FastAPI(
    title="AI Resume Analyzer API",
    description="API for analyzing resumes and matching them with job descriptions",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Database initialization
@app.on_event("startup")
async def start_db():
    # Create motor client
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URL)
    
    # Initialize beanie with the Product document class
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            Resume,
            JobDescription,
            ResumeJobMatch
        ]
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to the AI Resume Analyzer API",
        "docs_url": "/docs",
        "status": "online"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include API routers
app.include_router(resume_router.router, prefix=f"{settings.API_V1_STR}/resumes", tags=["resumes"])
app.include_router(job_router.router, prefix=f"{settings.API_V1_STR}/jobs", tags=["jobs"])
app.include_router(analysis_router.router, prefix=f"{settings.API_V1_STR}/analysis", tags=["analysis"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 