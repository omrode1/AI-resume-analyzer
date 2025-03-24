from typing import List
from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.models.job import JobDescription, Requirement
from app.services.job_parser import JobParser

router = APIRouter()
job_parser = JobParser()

class JobInput(BaseModel):
    title: str = None
    company: str = None
    text: str

@router.post("/", response_description="Create a new job description")
async def create_job(job_input: JobInput):
    """
    Create a new job description.
    If only the text is provided, the system will parse the job description to extract structured information.
    """
    try:
        # Parse job description text
        parsed_job = job_parser.parse_job(job_input.text)
        
        # Use input title and company if provided, otherwise use parsed values
        title = job_input.title if job_input.title else parsed_job.get("title", "Untitled Position")
        company = job_input.company if job_input.company else parsed_job.get("company", "Unknown Company")
        
        # Create job description document
        job = JobDescription(
            title=title,
            company=company,
            location=parsed_job.get("location"),
            job_type=parsed_job.get("job_type"),
            remote=parsed_job.get("remote", False),
            description=parsed_job.get("description", ""),
            responsibilities=parsed_job.get("responsibilities", []),
            requirements=[
                Requirement(**req) if isinstance(req, dict) else Requirement(description=req, category="General")
                for req in parsed_job.get("requirements", [])
            ],
            preferred_qualifications=parsed_job.get("preferred_qualifications", []),
            skills=parsed_job.get("skills", []),
            keywords=parsed_job.get("keywords", []),
            min_experience_years=parsed_job.get("min_experience_years"),
            education_level=parsed_job.get("education_level"),
            salary_range=parsed_job.get("salary_range"),
            raw_text=job_input.text
        )
        
        # Save to database
        await job.save()
        
        return job
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing job description: {str(e)}"
        )

@router.get("/", response_description="List all job descriptions")
async def list_jobs():
    """
    Retrieve a list of all job descriptions.
    """
    jobs = await JobDescription.find_all().to_list()
    return jobs

@router.get("/{id}", response_description="Get a job description by ID")
async def get_job(id: str):
    """
    Retrieve a specific job description by its ID.
    """
    job = await JobDescription.get(id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description with ID {id} not found"
        )
    return job

@router.delete("/{id}", response_description="Delete a job description")
async def delete_job(id: str):
    """
    Delete a job description by its ID.
    """
    job = await JobDescription.get(id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description with ID {id} not found"
        )
    
    # Delete from database
    await job.delete()
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Job description deleted successfully"})

@router.put("/{id}", response_description="Update a job description")
async def update_job(id: str, job_update: dict = Body(...)):
    """
    Update a job description by its ID.
    """
    job = await JobDescription.get(id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description with ID {id} not found"
        )
    
    # Update only the fields that are provided
    update_data = {k: v for k, v in job_update.items() if v is not None}
    
    # Handle special cases for nested objects
    if "requirements" in update_data:
        update_data["requirements"] = [
            Requirement(**req) if isinstance(req, dict) else Requirement(description=req, category="General")
            for req in update_data["requirements"]
        ]
    
    # Apply updates
    for key, value in update_data.items():
        setattr(job, key, value)
    
    # Save updates
    await job.save()
    
    return job

@router.get("/company/{name}", response_description="Search jobs by company name")
async def search_jobs_by_company(name: str):
    """
    Search for job descriptions by company name.
    Uses a case-insensitive partial match.
    """
    jobs = await JobDescription.find({"company": {"$regex": name, "$options": "i"}}).to_list()
    return jobs

@router.get("/title/{title}", response_description="Search jobs by title")
async def search_jobs_by_title(title: str):
    """
    Search for job descriptions by title.
    Uses a case-insensitive partial match.
    """
    jobs = await JobDescription.find({"title": {"$regex": title, "$options": "i"}}).to_list()
    return jobs 