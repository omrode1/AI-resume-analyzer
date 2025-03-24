import re
import spacy
from typing import Dict, List, Optional, Tuple
import nltk
from nltk.tokenize import sent_tokenize

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class JobParser:
    """Service to parse job descriptions and extract structured information."""
    
    def __init__(self):
        self.nlp = None
    
    def _load_spacy_model(self):
        if self.nlp is None:
            # Load the spaCy model
            self.nlp = spacy.load("en_core_web_md")
    
    def parse_job(self, text: str) -> Dict:
        """Parse job description text and extract structured information."""
        self._load_spacy_model()
        
        # Process the text with spaCy
        doc = self.nlp(text)
        
        # Extract basic information
        result = {
            "title": self._extract_title(doc, text),
            "company": self._extract_company(doc, text),
            "location": self._extract_location(doc, text),
            "job_type": self._extract_job_type(text),
            "remote": self._is_remote(text),
            "description": self._extract_description(text),
            "responsibilities": self._extract_responsibilities(text),
            "requirements": self._extract_requirements(text),
            "preferred_qualifications": self._extract_preferred_qualifications(text),
            "skills": self._extract_skills(doc, text),
            "min_experience_years": self._extract_experience_years(text),
            "education_level": self._extract_education_level(text),
            "salary_range": self._extract_salary_range(text),
            "raw_text": text
        }
        
        return result
    
    def _extract_title(self, doc, text: str) -> Optional[str]:
        """Extract job title from job description."""
        # Common job title patterns
        title_patterns = [
            r'(?i)job title:?\s*([A-Za-z0-9\s\-\/\,\&]+)(?:\r|\n|$)',
            r'(?i)position:?\s*([A-Za-z0-9\s\-\/\,\&]+)(?:\r|\n|$)',
            r'(?i)role:?\s*([A-Za-z0-9\s\-\/\,\&]+)(?:\r|\n|$)'
        ]
        
        # Try pattern matching first
        for pattern in title_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # If pattern matching fails, try using first line
        first_line = text.strip().split('\n')[0].strip()
        if len(first_line) < 100:  # reasonable title length
            return first_line
        
        return None
    
    def _extract_company(self, doc, text: str) -> Optional[str]:
        """Extract company name from job description."""
        # Look for ORG entities
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # Exclude common non-company organizations in job descriptions
                excluded_orgs = ["linkedin", "indeed", "glassdoor", "ziprecruiter"]
                if ent.text.lower() not in excluded_orgs:
                    return ent.text
        
        # Try pattern matching for company
        company_patterns = [
            r'(?i)company:?\s*([A-Za-z0-9\s\-\/\,\&\.]+)(?:\r|\n|$)',
            r'(?i)at\s+([A-Za-z0-9\s\-\/\,\&\.]+?)(?:,|\.|we|\s+is|\s+are|\r|\n|$)'
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_location(self, doc, text: str) -> Optional[str]:
        """Extract job location from job description."""
        # Look for location patterns
        location_patterns = [
            r'(?i)location:?\s*([A-Za-z0-9\s\-\/\,\&\.]+)(?:\r|\n|$)',
            r'(?i)based in:?\s*([A-Za-z0-9\s\-\/\,\&\.]+)(?:\r|\n|$)'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # Look for GPE (geopolitical entity) entities
        for ent in doc.ents:
            if ent.label_ == "GPE":
                return ent.text
        
        return None
    
    def _extract_job_type(self, text: str) -> Optional[str]:
        """Extract job type from job description (e.g., Full-time, Part-time)."""
        job_types = ["full-time", "part-time", "contract", "temporary", "internship", "freelance"]
        
        for job_type in job_types:
            pattern = r'\b' + re.escape(job_type) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                return job_type.title()
        
        # Default to full-time if not specified
        return "Full-time"
    
    def _is_remote(self, text: str) -> bool:
        """Determine if the job is remote."""
        remote_patterns = [
            r'\bremote\b',
            r'\bwork from home\b',
            r'\bwfh\b',
            r'\btelework\b',
            r'\bvirtual\b'
        ]
        
        for pattern in remote_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _extract_description(self, text: str) -> str:
        """Extract the general job description."""
        description_section = self._find_section(text, ["about the role", "about the position", "job description", "what you'll do", "overview"])
        
        if description_section:
            return description_section
        
        # If no clear description section, return the first few sentences
        sentences = sent_tokenize(text)
        return " ".join(sentences[:3])
    
    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract job responsibilities."""
        responsibilities_section = self._find_section(text, ["responsibilities", "duties", "what you'll do", "key tasks", "day to day"])
        
        if not responsibilities_section:
            return []
        
        return self._extract_bullet_points(responsibilities_section)
    
    def _extract_requirements(self, text: str) -> List[Dict]:
        """Extract job requirements."""
        requirements_section = self._find_section(text, ["requirements", "qualifications", "what you need", "skills required", "minimum qualifications"])
        
        if not requirements_section:
            return []
        
        bullet_points = self._extract_bullet_points(requirements_section)
        
        # Convert bullet points to requirement objects
        requirements = []
        for point in bullet_points:
            requirement = {
                "description": point,
                "category": self._categorize_requirement(point),
                "is_mandatory": self._is_mandatory_requirement(point)
            }
            requirements.append(requirement)
        
        return requirements
    
    def _categorize_requirement(self, requirement: str) -> str:
        """Categorize a requirement as Technical, Experience, Education, or Soft."""
        requirement_lower = requirement.lower()
        
        if any(edu in requirement_lower for edu in ["degree", "bachelor", "master", "phd", "education", "university", "college"]):
            return "Education"
        
        if any(exp in requirement_lower for exp in ["experience", "years", "worked", "previous"]):
            return "Experience"
        
        if any(soft in requirement_lower for soft in ["communication", "teamwork", "collaborate", "interpersonal", "problem-solving", "leadership"]):
            return "Soft"
        
        return "Technical"
    
    def _is_mandatory_requirement(self, requirement: str) -> bool:
        """Determine if a requirement is mandatory or preferred."""
        requirement_lower = requirement.lower()
        
        if any(preferred in requirement_lower for preferred in ["preferred", "nice to have", "bonus", "plus", "ideal", "desirable"]):
            return False
        
        return True
    
    def _extract_preferred_qualifications(self, text: str) -> List[str]:
        """Extract preferred qualifications."""
        preferred_section = self._find_section(text, ["preferred", "nice to have", "bonus", "plus", "ideal", "desirable"])
        
        if not preferred_section:
            return []
        
        return self._extract_bullet_points(preferred_section)
    
    def _extract_skills(self, doc, text: str) -> List[str]:
        """Extract required skills from job description."""
        # This is a simplified implementation
        # A more comprehensive solution would use a skills database/taxonomy
        
        # Common skills keywords
        technical_skills = [
            "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "php",
            "html", "css", "sql", "nosql", "mongodb", "mysql", "postgresql",
            "react", "angular", "vue", "node.js", "express", "django", "flask",
            "aws", "azure", "gcp", "docker", "kubernetes", "ci/cd", "git",
            "machine learning", "deep learning", "nlp", "computer vision",
            "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy"
        ]
        
        # Extract skills from text
        skills = []
        for skill in technical_skills:
            # Use word boundaries to match whole words
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                skills.append(skill)
        
        return skills
    
    def _extract_experience_years(self, text: str) -> Optional[int]:
        """Extract required years of experience."""
        # Look for patterns like "X+ years of experience" or "X-Y years of experience"
        experience_patterns = [
            r'(\d+)\+?\s*(?:-\s*\d+)?\s*years?\s*(?:of)?\s*experience',
            r'minimum\s*(?:of)?\s*(\d+)\s*years?\s*(?:of)?\s*experience',
            r'at\s*least\s*(\d+)\s*years?\s*(?:of)?\s*experience'
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
        
        return None
    
    def _extract_education_level(self, text: str) -> Optional[str]:
        """Extract required education level."""
        education_levels = {
            "high school": "High School",
            "associate": "Associate's",
            "bachelor": "Bachelor's",
            "master": "Master's",
            "phd": "PhD",
            "doctorate": "PhD",
            "mba": "MBA"
        }
        
        for level_key, level_value in education_levels.items():
            if re.search(r'\b' + re.escape(level_key) + r'\b', text, re.IGNORECASE):
                return level_value
        
        return None
    
    def _extract_salary_range(self, text: str) -> Optional[str]:
        """Extract salary range information."""
        # Look for patterns like "$X-$Y", "$X to $Y", "$X - $Y"
        salary_patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:-|to)\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:-|to)\s*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:USD|dollars)',
            r'salary range:?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:-|to)\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                min_salary = match.group(1)
                max_salary = match.group(2)
                return f"${min_salary} - ${max_salary}"
        
        return None
    
    def _extract_bullet_points(self, text: str) -> List[str]:
        """Extract bullet points from text."""
        # Split text into lines
        lines = text.split('\n')
        
        # Look for bullet point indicators
        bullet_points = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or line.startswith('*') or 
                         re.match(r'^\d+\.', line) or re.match(r'^\[\s*\]', line)):
                # Clean up the bullet point
                cleaned_line = re.sub(r'^[•\-\*\d\.\[\]\s]+\s*', '', line).strip()
                if cleaned_line:
                    bullet_points.append(cleaned_line)
        
        # If no bullet points found, try to split by sentences
        if not bullet_points:
            sentences = sent_tokenize(text)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 10 and len(sentence) < 200:
                    bullet_points.append(sentence)
        
        return bullet_points
    
    def _find_section(self, text: str, section_keywords: List[str]) -> Optional[str]:
        """Find a section in the job description based on keywords."""
        lines = text.split('\n')
        section_start = -1
        
        # Find the starting line of the section
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in section_keywords):
                section_start = i
                break
        
        if section_start == -1:
            return None
        
        # Find the end of the section (next section heading)
        section_end = len(lines)
        for i in range(section_start + 1, len(lines)):
            # Potential section headings are often short lines with uppercase letters
            if lines[i].strip() and len(lines[i]) < 50 and sum(1 for c in lines[i] if c.isupper()) > 2:
                section_end = i
                break
        
        # Return the section text
        return '\n'.join(lines[section_start:section_end]).strip() 