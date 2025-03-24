from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from beanie import Document

class SkillMatch(BaseModel):
    resume_skill: str
    job_skill: str
    score: float  # 0.0 to 1.0
    is_exact_match: bool

class CategoryScore(BaseModel):
    category: str  # e.g., "Skills", "Experience", "Education"
    score: float  # 0.0 to 1.0
    max_score: float
    weight: float  # How important this category is in the overall score
    details: Dict[str, float] = {}  # Additional scoring details

class ResumeJobMatch(Document):
    # Reference IDs
    resume_id: str
    job_id: str
    
    # Basic Info
    candidate_name: str
    job_title: str
    company: str
    
    # Match Scores
    overall_score: float  # 0.0 to 1.0
    category_scores: List[CategoryScore] = []
    
    # Detailed Matches
    skill_matches: List[SkillMatch] = []
    experience_relevance: Dict[str, float] = {}  # Maps experience titles to relevance scores
    
    # Missing Requirements
    missing_skills: List[str] = []
    missing_experience: List[str] = []
    missing_education: List[str] = []
    
    # Recommendations
    improvement_suggestions: List[str] = []
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "resume_job_matches"
        
    class Config:
        schema_extra = {
            "example": {
                "resume_id": "60d21b4967d0d8992e610c85",
                "job_id": "60d21b4967d0d8992e610c86",
                "candidate_name": "John Doe",
                "job_title": "Senior Software Engineer",
                "company": "Tech Innovations Inc.",
                "overall_score": 0.85,
                "category_scores": [
                    {
                        "category": "Skills",
                        "score": 0.90,
                        "max_score": 1.0,
                        "weight": 0.4,
                        "details": {
                            "technical_skills": 0.95,
                            "soft_skills": 0.85
                        }
                    },
                    {
                        "category": "Experience",
                        "score": 0.80,
                        "max_score": 1.0,
                        "weight": 0.35,
                        "details": {
                            "years_match": 0.85,
                            "role_relevance": 0.75
                        }
                    },
                    {
                        "category": "Education",
                        "score": 0.85,
                        "max_score": 1.0,
                        "weight": 0.25,
                        "details": {
                            "degree_match": 1.0,
                            "field_relevance": 0.70
                        }
                    }
                ],
                "skill_matches": [
                    {
                        "resume_skill": "Python",
                        "job_skill": "Python",
                        "score": 1.0,
                        "is_exact_match": True
                    },
                    {
                        "resume_skill": "React",
                        "job_skill": "React",
                        "score": 1.0,
                        "is_exact_match": True
                    },
                    {
                        "resume_skill": "TensorFlow",
                        "job_skill": "Machine Learning",
                        "score": 0.75,
                        "is_exact_match": False
                    }
                ],
                "experience_relevance": {
                    "Software Engineer": 0.85,
                    "Web Developer": 0.70
                },
                "missing_skills": ["Docker", "Kubernetes"],
                "missing_experience": ["Team leadership experience"],
                "missing_education": [],
                "improvement_suggestions": [
                    "Add Docker and Kubernetes to your skill set",
                    "Highlight any team leadership experience in your resume",
                    "Emphasize cloud platform experience"
                ]
            }
        } 