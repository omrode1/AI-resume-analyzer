import os
import re
import spacy
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

class MatchingEngine:
    """Service for matching resumes with job descriptions."""
    
    def __init__(self):
        self.nlp = None
        self.sentence_transformer = None
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    
    def _load_models(self):
        """Load NLP models when needed."""
        if self.nlp is None:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_md")
        
        if self.sentence_transformer is None:
            # Load Sentence Transformer model
            self.sentence_transformer = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    def match_resume_to_job(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Match a resume against a job description and return match scores."""
        self._load_models()
        
        # Calculate overall and category scores
        skill_match_results = self._match_skills(resume_data.get('skills', []), job_data.get('skills', []))
        experience_match_results = self._match_experience(resume_data, job_data)
        education_match_results = self._match_education(resume_data, job_data)
        
        # Calculate weighted overall score
        weights = {
            "skills": 0.4,
            "experience": 0.35,
            "education": 0.25
        }
        
        overall_score = (
            weights["skills"] * skill_match_results["score"] +
            weights["experience"] * experience_match_results["score"] +
            weights["education"] * education_match_results["score"]
        )
        
        # Format the category scores
        category_scores = [
            {
                "category": "Skills",
                "score": skill_match_results["score"],
                "max_score": 1.0,
                "weight": weights["skills"],
                "details": skill_match_results["details"]
            },
            {
                "category": "Experience",
                "score": experience_match_results["score"],
                "max_score": 1.0,
                "weight": weights["experience"],
                "details": experience_match_results["details"]
            },
            {
                "category": "Education",
                "score": education_match_results["score"],
                "max_score": 1.0,
                "weight": weights["education"],
                "details": education_match_results["details"]
            }
        ]
        
        # Identify missing requirements
        missing_skills = [skill for skill in job_data.get('skills', []) 
                         if skill not in [match["job_skill"] for match in skill_match_results["skill_matches"] 
                                         if match["score"] > 0.7]]
        
        # Generate improvement suggestions
        improvement_suggestions = self._generate_improvement_suggestions(missing_skills, 
                                                                       experience_match_results, 
                                                                       education_match_results)
        
        # Construct match results
        match_results = {
            "resume_id": str(resume_data.get('_id', '')),
            "job_id": str(job_data.get('_id', '')),
            "candidate_name": resume_data.get('candidate_name', ''),
            "job_title": job_data.get('title', ''),
            "company": job_data.get('company', ''),
            "overall_score": round(overall_score, 2),
            "category_scores": category_scores,
            "skill_matches": skill_match_results["skill_matches"],
            "experience_relevance": experience_match_results["experience_relevance"],
            "missing_skills": missing_skills,
            "missing_experience": experience_match_results.get("missing_experience", []),
            "missing_education": education_match_results.get("missing_education", []),
            "improvement_suggestions": improvement_suggestions
        }
        
        return match_results
    
    def _match_skills(self, resume_skills: List[str], job_skills: List[str]) -> Dict:
        """Match skills from resume with job skills."""
        if not resume_skills or not job_skills:
            return {
                "score": 0.0,
                "details": {},
                "skill_matches": []
            }
        
        # Normalize skills to lowercase
        resume_skills_lower = [skill.lower() for skill in resume_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Calculate exact matches
        exact_matches = [skill for skill in resume_skills_lower if skill in job_skills_lower]
        exact_match_score = len(exact_matches) / len(job_skills_lower) if job_skills_lower else 0
        
        # Calculate semantic matches for non-exact matches
        skill_matches = []
        
        # Process exact matches first
        for resume_skill in resume_skills:
            resume_skill_lower = resume_skill.lower()
            if resume_skill_lower in job_skills_lower:
                matching_job_skill = next(skill for skill in job_skills if skill.lower() == resume_skill_lower)
                skill_matches.append({
                    "resume_skill": resume_skill,
                    "job_skill": matching_job_skill,
                    "score": 1.0,
                    "is_exact_match": True
                })
        
        # For non-exact matches, use NLP to find similar skills
        remaining_resume_skills = [skill for skill in resume_skills if skill.lower() not in exact_matches]
        
        if remaining_resume_skills and job_skills:
            # Get embeddings for remaining skills
            resume_skill_embeddings = [self.nlp(skill).vector for skill in remaining_resume_skills]
            job_skill_embeddings = [self.nlp(skill).vector for skill in job_skills]
            
            # Calculate similarity between each remaining resume skill and job skills
            for i, resume_skill in enumerate(remaining_resume_skills):
                best_match_idx = -1
                best_match_score = 0
                
                for j, job_skill in enumerate(job_skills):
                    similarity = cosine_similarity(
                        [resume_skill_embeddings[i]], 
                        [job_skill_embeddings[j]]
                    )[0][0]
                    
                    if similarity > best_match_score and similarity > 0.5:  # Only consider matches above threshold
                        best_match_score = similarity
                        best_match_idx = j
                
                if best_match_idx != -1:
                    skill_matches.append({
                        "resume_skill": resume_skill,
                        "job_skill": job_skills[best_match_idx],
                        "score": float(best_match_score),
                        "is_exact_match": False
                    })
        
        # Calculate semantic match score (weighted average of all matches)
        semantic_match_score = 0
        if skill_matches:
            total_weight = len(job_skills)
            weighted_sum = sum(match["score"] for match in skill_matches)
            semantic_match_score = weighted_sum / total_weight
        
        # Calculate final skill score (50% exact matches, 50% semantic matches)
        final_score = 0.5 * exact_match_score + 0.5 * semantic_match_score
        
        return {
            "score": final_score,
            "details": {
                "exact_match_score": exact_match_score,
                "semantic_match_score": semantic_match_score,
                "exact_matches": len(exact_matches),
                "total_job_skills": len(job_skills_lower),
                "total_resume_skills": len(resume_skills_lower)
            },
            "skill_matches": skill_matches
        }
    
    def _match_experience(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Match experience from resume with job requirements."""
        # Get years of experience from resume
        resume_experience = resume_data.get('experience', [])
        required_years = job_data.get('min_experience_years', 0)
        
        # Calculate total years of experience
        total_years = 0
        experience_relevance = {}
        
        for exp in resume_experience:
            # Try to extract years from dates
            years = self._calculate_experience_years(exp.get('dates', ''))
            
            # Get position and company
            position = exp.get('position', '')
            company = exp.get('company', '')
            
            if position:
                # Calculate relevance score for each position
                relevance_score = self._calculate_relevance_score(
                    position, 
                    job_data.get('title', ''), 
                    job_data.get('description', '')
                )
                experience_relevance[position] = relevance_score
            
            total_years += years
        
        # Calculate years match score (capped at 100%)
        years_match = min(1.0, total_years / required_years) if required_years > 0 else 1.0
        
        # Calculate role relevance (average of all positions)
        avg_relevance = sum(experience_relevance.values()) / len(experience_relevance) if experience_relevance else 0
        
        # Calculate experience score (70% years match, 30% role relevance)
        experience_score = 0.7 * years_match + 0.3 * avg_relevance
        
        # Determine if there's missing experience
        missing_experience = []
        if total_years < required_years:
            missing_experience.append(f"Need {required_years - total_years} more years of relevant experience")
        
        # Get job responsibilities
        job_responsibilities = job_data.get('responsibilities', [])
        
        # Check if resume experience covers job responsibilities
        if job_responsibilities:
            # Get all experience descriptions
            resume_exp_descriptions = []
            for exp in resume_experience:
                if 'description' in exp and exp['description']:
                    resume_exp_descriptions.append(exp['description'])
            
            # Combine all experience descriptions
            combined_exp_text = " ".join(resume_exp_descriptions)
            
            # Check each responsibility
            for resp in job_responsibilities:
                # Calculate semantic similarity
                similarity = self._calculate_text_similarity(combined_exp_text, resp)
                
                # If similarity is below threshold, add to missing experience
                if similarity < 0.5:
                    missing_experience.append(f"Missing experience: {resp}")
        
        return {
            "score": experience_score,
            "details": {
                "years_match": years_match,
                "role_relevance": avg_relevance,
                "total_years": total_years,
                "required_years": required_years
            },
            "experience_relevance": experience_relevance,
            "missing_experience": missing_experience
        }
    
    def _match_education(self, resume_data: Dict, job_data: Dict) -> Dict:
        """Match education from resume with job requirements."""
        resume_education = resume_data.get('education', [])
        required_education = job_data.get('education_level', '')
        
        # Education level hierarchy
        education_levels = {
            "High School": 1,
            "Associate's": 2, 
            "Bachelor's": 3,
            "Master's": 4,
            "MBA": 4,
            "PhD": 5,
            "Doctorate": 5
        }
        
        # Get the highest education level from the resume
        highest_edu_level = 0
        degree_names = []
        institutions = []
        
        for edu in resume_education:
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            
            if degree:
                degree_names.append(degree)
                
                # Determine education level
                for level_name, level_value in education_levels.items():
                    if level_name.lower() in degree.lower():
                        highest_edu_level = max(highest_edu_level, level_value)
                        break
            
            if institution:
                institutions.append(institution)
        
        # Calculate degree match score
        degree_match = 0
        missing_education = []
        
        if required_education:
            required_level = education_levels.get(required_education, 0)
            
            if highest_edu_level >= required_level:
                degree_match = 1.0
            else:
                degree_match = highest_edu_level / required_level if required_level > 0 else 0
                missing_education.append(f"Need {required_education} degree or equivalent")
        else:
            # If no specific education requirement, assume it's satisfied
            degree_match = 1.0
        
        # Calculate field relevance if job title and degree fields are available
        field_relevance = 0
        if degree_names and job_data.get('title', ''):
            job_title = job_data.get('title', '')
            
            # Get relevant fields based on job title
            relevant_fields = []
            if "engineer" in job_title.lower() or "developer" in job_title.lower():
                relevant_fields = ["computer science", "software engineering", "information technology", "computer engineering"]
            elif "data" in job_title.lower() or "analyst" in job_title.lower():
                relevant_fields = ["data science", "statistics", "mathematics", "analytics", "computer science"]
            # Add more field mappings as needed
            
            # Check if any degree is in a relevant field
            for degree in degree_names:
                degree_lower = degree.lower()
                for field in relevant_fields:
                    if field in degree_lower:
                        field_relevance = 1.0
                        break
                
                if field_relevance > 0:
                    break
            
            # If no exact field match, calculate semantic similarity
            if field_relevance == 0 and relevant_fields:
                max_similarity = 0
                for degree in degree_names:
                    for field in relevant_fields:
                        similarity = self._calculate_text_similarity(degree, field)
                        max_similarity = max(max_similarity, similarity)
                
                field_relevance = max_similarity
        else:
            # If can't determine relevance, assume it's average
            field_relevance = 0.5
        
        # Calculate education score (70% degree match, 30% field relevance)
        education_score = 0.7 * degree_match + 0.3 * field_relevance
        
        return {
            "score": education_score,
            "details": {
                "degree_match": degree_match,
                "field_relevance": field_relevance,
                "highest_edu_level": highest_edu_level
            },
            "missing_education": missing_education
        }
    
    def _calculate_experience_years(self, date_str: str) -> float:
        """Calculate years of experience from a date range string."""
        if not date_str:
            return 0
        
        # Pattern for dates (e.g., 2018-2022, 2018 - Present, etc.)
        pattern = r'(\d{4})\s*-\s*((?:\d{4})|(?:Present|Current))'
        match = re.search(pattern, date_str, re.IGNORECASE)
        
        if not match:
            return 0
        
        start_year = int(match.group(1))
        
        if match.group(2).isdigit():
            end_year = int(match.group(2))
        else:
            # If end date is "Present" or "Current", use current year
            from datetime import datetime
            end_year = datetime.now().year
        
        return end_year - start_year
    
    def _calculate_relevance_score(self, resume_text: str, job_title: str, job_description: str) -> float:
        """Calculate relevance score between resume experience and job requirements."""
        if not resume_text or (not job_title and not job_description):
            return 0
        
        # Combine job title and description
        job_text = f"{job_title} {job_description}"
        
        # Calculate semantic similarity
        similarity = self._calculate_text_similarity(resume_text, job_text)
        
        return similarity
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        if not text1 or not text2:
            return 0
        
        # For short texts, use Sentence Transformers
        if len(text1) < 1000 and len(text2) < 1000:
            embed1 = self.sentence_transformer.encode([text1])[0]
            embed2 = self.sentence_transformer.encode([text2])[0]
            
            # Calculate cosine similarity
            similarity = np.dot(embed1, embed2) / (np.linalg.norm(embed1) * np.linalg.norm(embed2))
            return float(similarity)
        
        # For longer texts, use TF-IDF vectorization
        else:
            tfidf_matrix = self.tfidf_vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
    
    def _generate_improvement_suggestions(self, missing_skills: List[str], 
                                        experience_results: Dict, 
                                        education_results: Dict) -> List[str]:
        """Generate suggestions for improving resume for better job match."""
        suggestions = []
        
        # Suggest adding missing skills
        if missing_skills:
            if len(missing_skills) <= 3:
                suggestions.append(f"Add {', '.join(missing_skills)} to your skill set")
            else:
                suggestions.append(f"Add {', '.join(missing_skills[:3])} and other missing skills to your skill set")
        
        # Suggest experience improvements
        if experience_results.get("missing_experience", []):
            for exp in experience_results["missing_experience"][:2]:  # Limit to top 2
                suggestions.append(exp)
        
        # Suggest education improvements
        if education_results.get("missing_education", []):
            for edu in education_results["missing_education"]:
                suggestions.append(edu)
        
        return suggestions 