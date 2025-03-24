import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Resume API endpoints
export const resumeApi = {
  // Upload a resume file
  uploadResume: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // Get all resumes
  getAllResumes: () => api.get('/resumes'),
  
  // Get resume by ID
  getResumeById: (id) => api.get(`/resumes/${id}`),
  
  // Delete resume
  deleteResume: (id) => api.delete(`/resumes/${id}`),
  
  // Search resumes by candidate name
  searchResumesByName: (name) => api.get(`/resumes/candidate/${name}`),
};

// Job API endpoints
export const jobApi = {
  // Create a new job description
  createJob: (jobData) => api.post('/jobs', jobData),
  
  // Get all jobs
  getAllJobs: () => api.get('/jobs'),
  
  // Get job by ID
  getJobById: (id) => api.get(`/jobs/${id}`),
  
  // Update job
  updateJob: (id, jobData) => api.put(`/jobs/${id}`, jobData),
  
  // Delete job
  deleteJob: (id) => api.delete(`/jobs/${id}`),
  
  // Search jobs by company
  searchJobsByCompany: (company) => api.get(`/jobs/company/${company}`),
  
  // Search jobs by title
  searchJobsByTitle: (title) => api.get(`/jobs/title/${title}`),
};

// Analysis API endpoints
export const analysisApi = {
  // Match a resume with a job
  matchResumeToJob: (resumeId, jobId) => api.post('/analysis/match', { resume_id: resumeId, job_id: jobId }),
  
  // Get all matches
  getAllMatches: () => api.get('/analysis'),
  
  // Get match by ID
  getMatchById: (id) => api.get(`/analysis/${id}`),
  
  // Delete match
  deleteMatch: (id) => api.delete(`/analysis/${id}`),
  
  // Get matches for a resume
  getMatchesByResume: (resumeId) => api.get(`/analysis/resume/${resumeId}`),
  
  // Get matches for a job
  getMatchesByJob: (jobId) => api.get(`/analysis/job/${jobId}`),
  
  // Get top candidates for a job
  getTopCandidates: (jobId, limit = 10) => api.get(`/analysis/top-candidates/${jobId}?limit=${limit}`),
  
  // Get best job matches for a resume
  getBestMatches: (resumeId, limit = 10) => api.get(`/analysis/best-matches/${resumeId}?limit=${limit}`),
};

export default {
  resume: resumeApi,
  job: jobApi,
  analysis: analysisApi,
}; 