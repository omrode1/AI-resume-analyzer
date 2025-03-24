import os
import re
import spacy
from typing import Dict, List, Optional, Tuple
import PyPDF2
import docx
from pdfminer.high_level import extract_text as pdfminer_extract_text

# We'll load spaCy model when needed to save memory
# nlp = spacy.load("en_core_web_md")

class ResumeParser:
    """Service to parse resume documents and extract structured information."""
    
    def __init__(self):
        self.nlp = None
    
    def _load_spacy_model(self):
        if self.nlp is None:
            # Load the spaCy model
            self.nlp = spacy.load("en_core_web_md")
    
    def extract_text(self, file_path: str) -> str:
        """Extract text from a resume file (PDF or DOCX)."""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif file_ext == '.docx':
            return self._extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            # Try with PyPDF2 first
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                if text.strip():
                    return text
                
            # If PyPDF2 fails or returns empty text, try with pdfminer
            return pdfminer_extract_text(file_path)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            raise
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from a DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            raise
    
    def parse_resume(self, text: str) -> Dict:
        """Parse resume text and extract structured information."""
        self._load_spacy_model()
        
        # Process the text with spaCy
        doc = self.nlp(text)
        
        # Extract basic information
        result = {
            "candidate_name": self._extract_name(doc, text),
            "email": self._extract_email(text),
            "phone": self._extract_phone(text),
            "location": self._extract_location(doc, text),
            "links": self._extract_links(text),
            "skills": self._extract_skills(doc, text),
            "education": self._extract_education(doc, text),
            "experience": self._extract_experience(doc, text),
            "summary": self._extract_summary(doc, text),
            "raw_text": text
        }
        
        return result
    
    def _extract_name(self, doc, text: str) -> Optional[str]:
        """Extract candidate name from resume."""
        # Basic implementation - can be improved
        # Assumption: Name might be at the beginning of the document
        # or in a section with keywords like "name", "profile", etc.
        
        # Check first few sentences for potential names
        for sent in list(doc.sents)[:3]:
            for ent in sent.ents:
                if ent.label_ == "PERSON":
                    return ent.text
        
        # If no name found, return first line as a fallback
        first_line = text.strip().split('\n')[0].strip()
        if first_line and len(first_line) > 0 and len(first_line.split()) <= 5:
            return first_line
        
        return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from resume."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from resume."""
        # Pattern to match various phone number formats
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else None
    
    def _extract_location(self, doc, text: str) -> Optional[str]:
        """Extract location from resume."""
        # Look for GPE (geopolitical entity) entities
        for ent in doc.ents:
            if ent.label_ == "GPE":
                return ent.text
        return None
    
    def _extract_links(self, text: str) -> Dict[str, str]:
        """Extract links (LinkedIn, GitHub, personal website) from resume."""
        links = {
            "linkedin": None,
            "github": None,
            "website": None
        }
        
        # LinkedIn pattern
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9_-]+'
        linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_match:
            links["linkedin"] = linkedin_match.group(0)
        
        # GitHub pattern
        github_pattern = r'github\.com/[A-Za-z0-9_-]+'
        github_match = re.search(github_pattern, text, re.IGNORECASE)
        if github_match:
            links["github"] = github_match.group(0)
        
        # Website pattern
        website_pattern = r'https?://(?!linkedin\.com|github\.com)[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
        website_match = re.search(website_pattern, text, re.IGNORECASE)
        if website_match:
            links["website"] = website_match.group(0)
        
        return links
    
    def _extract_skills(self, doc, text: str) -> List[str]:
        """Extract skills from resume."""
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
    
    def _extract_education(self, doc, text: str) -> List[Dict]:
        """Extract education information from resume."""
        # Find education section
        education_section = self._find_section(text, ["education", "academic", "qualification"])
        
        if not education_section:
            return []
        
        # Simple pattern to extract degree, institution and dates
        education = []
        
        # Simple pattern matching for degrees
        degree_pattern = r'(Bachelor|Master|Ph\.D|MBA|B\.S|M\.S|B\.A|M\.A)\.?\s+(of|in)?\s+([A-Za-z\s]+)'
        institution_pattern = r'(University|College|Institute|School) of ([A-Za-z\s]+)'
        
        degree_matches = re.finditer(degree_pattern, education_section, re.IGNORECASE)
        for match in degree_matches:
            education.append({
                "degree": match.group(0),
                "institution": self._find_closest_institution(education_section, match.start()),
                "dates": self._extract_dates_near_match(education_section, match.start())
            })
        
        return education
    
    def _find_closest_institution(self, text: str, position: int) -> Optional[str]:
        """Find the closest institution name to a given position in text."""
        institution_pattern = r'(University|College|Institute|School) of ([A-Za-z\s]+)'
        matches = list(re.finditer(institution_pattern, text, re.IGNORECASE))
        
        if not matches:
            return None
        
        # Find closest match
        closest_match = min(matches, key=lambda m: abs(m.start() - position))
        return closest_match.group(0)
    
    def _extract_dates_near_match(self, text: str, position: int, window: int = 200) -> Optional[str]:
        """Extract dates near a given position in text."""
        # Get text window around position
        start = max(0, position - window // 2)
        end = min(len(text), position + window // 2)
        window_text = text[start:end]
        
        # Pattern for dates (e.g., 2018-2022, 2018 - 2022, etc.)
        date_pattern = r'\b(20\d{2})\s*-\s*(20\d{2}|Present|Current)\b'
        match = re.search(date_pattern, window_text, re.IGNORECASE)
        
        return match.group(0) if match else None
    
    def _extract_experience(self, doc, text: str) -> List[Dict]:
        """Extract work experience information from resume."""
        experience_section = self._find_section(text, ["experience", "employment", "work history"])
        
        if not experience_section:
            return []
        
        experience = []
        
        # Extract companies and positions
        # This is a simplified implementation
        for ent in doc.ents:
            if ent.label_ == "ORG" and ent.text.lower() in experience_section.lower():
                experience.append({
                    "company": ent.text,
                    "position": self._find_position_near_company(experience_section, ent.text),
                    "dates": self._extract_dates_near_match(experience_section, experience_section.lower().find(ent.text.lower()))
                })
        
        return experience
    
    def _find_position_near_company(self, text: str, company: str) -> Optional[str]:
        """Find a job position near a company mention in text."""
        # Common job titles
        job_titles = [
            "Engineer", "Developer", "Manager", "Director", "Analyst", "Specialist",
            "Coordinator", "Administrator", "Assistant", "Associate", "Lead", "Senior"
        ]
        
        # Find the company in the text
        company_pos = text.lower().find(company.lower())
        if company_pos == -1:
            return None
        
        # Look for job titles in the surrounding context
        start = max(0, company_pos - 100)
        end = min(len(text), company_pos + 100)
        context = text[start:end]
        
        for title in job_titles:
            if title.lower() in context.lower():
                # Extract the full job title (not just the keyword)
                pos = context.lower().find(title.lower())
                
                # Try to extract a complete job title (up to 5 words)
                words = context[max(0, pos-30):pos+50].split()
                title_index = -1
                
                for i, word in enumerate(words):
                    if title.lower() in word.lower():
                        title_index = i
                        break
                
                if title_index != -1:
                    # Take up to 5 words around the title keyword
                    start_index = max(0, title_index - 2)
                    end_index = min(len(words), title_index + 3)
                    return " ".join(words[start_index:end_index])
                
                return title
        
        return None
    
    def _extract_summary(self, doc, text: str) -> Optional[str]:
        """Extract summary or objective statement from resume."""
        summary_section = self._find_section(text, ["summary", "objective", "profile", "about me"])
        
        if not summary_section:
            # If no specific summary section, use the first paragraph
            paragraphs = text.split('\n\n')
            if paragraphs:
                return paragraphs[0].strip()
        else:
            # Use the first paragraph of the summary section
            paragraphs = summary_section.split('\n\n')
            if paragraphs:
                return paragraphs[0].strip()
        
        return None
    
    def _find_section(self, text: str, section_keywords: List[str]) -> Optional[str]:
        """Find a section in the resume based on keywords."""
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