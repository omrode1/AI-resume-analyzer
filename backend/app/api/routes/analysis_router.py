from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.models.resume import Resume
from app.models.job import JobDescription
from app.models.analysis import ResumeJobMatch
from app.services.matching_engine import MatchingEngine

router = APIRouter()
matching_engine = MatchingEngine()

class MatchRequest(BaseModel):
    resume_id: str
    job_id: str

@router.post("/match", response_description="Match a resume with a job description")
async def match_resume_to_job(match_request: MatchRequest):
    """
    Analyze and match a resume with a job description.
    Returns detailed match scores and analysis.
    """
    # Retrieve resume and job documents
    resume = await Resume.get(match_request.resume_id)
    job = await JobDescription.get(match_request.job_id)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {match_request.resume_id} not found"
        )
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job description with ID {match_request.job_id} not found"
        )
    
    try:
        # Check if match already exists
        existing_match = await ResumeJobMatch.find_one(
            {"resume_id": match_request.resume_id, "job_id": match_request.job_id}
        )
        
        if existing_match:
            # Update the timestamp instead of creating a new match
            existing_match.updated_at = None  # Let Beanie update it automatically
            await existing_match.save()
            return existing_match
        
        # Perform matching
        match_results = matching_engine.match_resume_to_job(resume.dict(), job.dict())
        
        # Create match document
        match = ResumeJobMatch(**match_results)
        
        # Save to database
        await match.save()
        
        return match
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing match: {str(e)}"
        )

@router.get("/", response_description="List all resume-job matches")
async def list_matches():
    """
    Retrieve a list of all resume-job matches.
    """
    matches = await ResumeJobMatch.find_all().to_list()
    return matches

@router.get("/{id}", response_description="Get a specific match by ID")
async def get_match(id: str):
    """
    Retrieve a specific resume-job match by its ID.
    """
    match = await ResumeJobMatch.get(id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {id} not found"
        )
    return match

@router.delete("/{id}", response_description="Delete a match")
async def delete_match(id: str):
    """
    Delete a resume-job match by its ID.
    """
    match = await ResumeJobMatch.get(id)
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {id} not found"
        )
    
    # Delete from database
    await match.delete()
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Match deleted successfully"})

@router.get("/resume/{resume_id}", response_description="Get matches for a specific resume")
async def get_matches_by_resume(resume_id: str):
    """
    Retrieve all job matches for a specific resume.
    """
    matches = await ResumeJobMatch.find({"resume_id": resume_id}).to_list()
    return matches

@router.get("/job/{job_id}", response_description="Get matches for a specific job")
async def get_matches_by_job(job_id: str):
    """
    Retrieve all resume matches for a specific job.
    """
    matches = await ResumeJobMatch.find({"job_id": job_id}).to_list()
    return matches

@router.get("/top-candidates/{job_id}", response_description="Get top candidate matches for a job")
async def get_top_candidates(job_id: str, limit: int = 10):
    """
    Retrieve the top candidate matches for a specific job, sorted by match score.
    """
    matches = await ResumeJobMatch.find({"job_id": job_id}).sort("overall_score", -1).limit(limit).to_list()
    return matches

@router.get("/best-matches/{resume_id}", response_description="Get best job matches for a candidate")
async def get_best_matches(resume_id: str, limit: int = 10):
    """
    Retrieve the best job matches for a specific resume, sorted by match score.
    """
    matches = await ResumeJobMatch.find({"resume_id": resume_id}).sort("overall_score", -1).limit(limit).to_list()
    return matches 