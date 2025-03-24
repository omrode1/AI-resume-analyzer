from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from beanie import Document

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None

class Experience(BaseModel):
    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    description: Optional[str] = None
    skills: List[str] = []

class Skill(BaseModel):
    name: str
    level: Optional[str] = None  # e.g., "Beginner", "Intermediate", "Expert"
    category: Optional[str] = None  # e.g., "Technical", "Soft", "Language"

class Resume(Document):
    # Personal Information
    candidate_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    
    # Career Summary
    summary: Optional[str] = None
    
    # Education
    education: List[Education] = []
    
    # Work Experience
    experience: List[Experience] = []
    
    # Skills
    skills: List[Skill] = []
    
    # Additional Information
    certifications: List[str] = []
    languages: List[str] = []
    interests: List[str] = []
    
    # File Information
    file_name: str
    file_path: str
    file_type: str  # PDF, DOCX, etc.
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Raw Content
    raw_text: str
    
    class Settings:
        name = "resumes"
        
    class Config:
        schema_extra = {
            "example": {
                "candidate_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "location": "New York, NY",
                "linkedin": "linkedin.com/in/johndoe",
                "github": "github.com/johndoe",
                "summary": "Experienced software engineer with a passion for AI and machine learning.",
                "education": [
                    {
                        "institution": "MIT",
                        "degree": "Bachelor of Science",
                        "field_of_study": "Computer Science",
                        "start_date": "2015-09-01T00:00:00",
                        "end_date": "2019-05-31T00:00:00"
                    }
                ],
                "experience": [
                    {
                        "company": "Tech Corp",
                        "title": "Software Engineer",
                        "location": "San Francisco, CA",
                        "start_date": "2019-06-01T00:00:00",
                        "end_date": "2022-12-31T00:00:00",
                        "description": "Developed and maintained web applications using React and Node.js.",
                        "skills": ["React", "Node.js", "JavaScript", "TypeScript"]
                    }
                ],
                "skills": [
                    {"name": "Python", "level": "Expert", "category": "Technical"},
                    {"name": "React", "level": "Intermediate", "category": "Technical"},
                    {"name": "Leadership", "level": "Advanced", "category": "Soft"}
                ],
                "certifications": ["AWS Certified Developer", "Google Cloud Professional"],
                "languages": ["English", "Spanish"],
                "interests": ["Open Source", "AI Research"],
                "file_name": "john_doe_resume.pdf",
                "file_path": "/uploads/john_doe_resume.pdf",
                "file_type": "PDF",
                "raw_text": "Full text content of the resume..."
            }
        } 