from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from beanie import Document

class Requirement(BaseModel):
    description: str
    category: Optional[str] = None  # e.g., "Technical", "Soft", "Experience", "Education"
    is_mandatory: bool = True

class JobDescription(Document):
    # Basic Info
    title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None  # e.g., "Full-time", "Part-time", "Contract"
    remote: bool = False
    
    # Details
    description: str
    responsibilities: List[str] = []
    requirements: List[Requirement] = []
    preferred_qualifications: List[str] = []
    
    # Skills and Keywords
    skills: List[str] = []
    keywords: List[str] = []
    
    # Extracted Information
    min_experience_years: Optional[int] = None
    education_level: Optional[str] = None  # e.g., "Bachelor's", "Master's", "PhD"
    salary_range: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    
    # Raw Content
    raw_text: str
    
    class Settings:
        name = "jobs"
        
    class Config:
        schema_extra = {
            "example": {
                "title": "Senior Software Engineer",
                "company": "Tech Innovations Inc.",
                "location": "San Francisco, CA",
                "job_type": "Full-time",
                "remote": True,
                "description": "We are looking for a Senior Software Engineer to join our team...",
                "responsibilities": [
                    "Design and develop high-quality software solutions",
                    "Collaborate with cross-functional teams",
                    "Mentor junior developers"
                ],
                "requirements": [
                    {
                        "description": "5+ years of experience in software development",
                        "category": "Experience",
                        "is_mandatory": True
                    },
                    {
                        "description": "Proficiency in Python and JavaScript",
                        "category": "Technical",
                        "is_mandatory": True
                    },
                    {
                        "description": "Experience with cloud platforms (AWS, GCP)",
                        "category": "Technical",
                        "is_mandatory": False
                    }
                ],
                "preferred_qualifications": [
                    "Experience with machine learning frameworks",
                    "Contributions to open-source projects"
                ],
                "skills": [
                    "Python", "JavaScript", "React", "AWS", "Docker", "CI/CD"
                ],
                "keywords": [
                    "software engineering", "full stack", "agile", "cloud"
                ],
                "min_experience_years": 5,
                "education_level": "Bachelor's",
                "salary_range": "$120,000 - $150,000",
                "is_active": True,
                "raw_text": "Full text content of the job description..."
            }
        } 