import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.core.config import settings
from app.models.resume import Resume
from app.services.resume_parser import ResumeParser

router = APIRouter()
resume_parser = ResumeParser()

@router.post("/upload", response_description="Upload a resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF or DOCX) and parse it.
    Returns the parsed resume data.
    """
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ['.pdf', '.docx']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF and DOCX files are accepted"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Extract text from the resume
        resume_text = resume_parser.extract_text(file_path)
        
        # Parse the resume text
        parsed_resume = resume_parser.parse_resume(resume_text)
        
        # Create resume document
        resume = Resume(
            candidate_name=parsed_resume.get("candidate_name", ""),
            email=parsed_resume.get("email"),
            phone=parsed_resume.get("phone"),
            location=parsed_resume.get("location"),
            linkedin=parsed_resume.get("links", {}).get("linkedin"),
            github=parsed_resume.get("links", {}).get("github"),
            website=parsed_resume.get("links", {}).get("website"),
            summary=parsed_resume.get("summary"),
            education=parsed_resume.get("education", []),
            experience=parsed_resume.get("experience", []),
            skills=[{"name": skill} for skill in parsed_resume.get("skills", [])],
            file_name=file.filename,
            file_path=file_path,
            file_type=file_ext.strip('.').upper(),
            raw_text=resume_text
        )
        
        # Save to database
        await resume.save()
        
        return resume
    
    except Exception as e:
        # Clean up the file if parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing resume: {str(e)}"
        )

@router.get("/", response_description="List all resumes")
async def list_resumes():
    """
    Retrieve a list of all uploaded resumes.
    """
    resumes = await Resume.find_all().to_list()
    return resumes

@router.get("/{id}", response_description="Get a resume by ID")
async def get_resume(id: str):
    """
    Retrieve a specific resume by its ID.
    """
    resume = await Resume.get(id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {id} not found"
        )
    return resume

@router.delete("/{id}", response_description="Delete a resume")
async def delete_resume(id: str):
    """
    Delete a resume by its ID.
    Also removes the associated file.
    """
    resume = await Resume.get(id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resume with ID {id} not found"
        )
    
    # Delete the file if it exists
    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)
    
    # Delete from database
    await resume.delete()
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Resume deleted successfully"})

@router.get("/candidate/{name}", response_description="Search resumes by candidate name")
async def search_resume_by_name(name: str):
    """
    Search for resumes by candidate name.
    Uses a case-insensitive partial match.
    """
    resumes = await Resume.find({"candidate_name": {"$regex": name, "$options": "i"}}).to_list()
    return resumes 