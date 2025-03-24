# AI Resume Analyzer

A web application that uses AI to analyze resumes, parse job descriptions, and match candidates with job positions based on skill compatibility.

## Features

- **Resume Parsing**: Upload and parse resumes in PDF or DOCX format to extract candidate information and skills.
- **Job Description Management**: Create and manage job descriptions with required skills.
- **Smart Matching**: AI-powered matching engine that compares candidate skills with job requirements.
- **Detailed Analysis**: View comprehensive match analysis with scores and skill comparisons.
- **Candidate Ranking**: Find the best candidates for a job position based on skill compatibility.
- **Job Recommendations**: Suggest suitable jobs for candidates based on their skills.

## Tech Stack

### Backend
- Python with FastAPI
- MongoDB for data storage
- PyMongo for database interaction
- Spacy and ML models for natural language processing
- PyPDF2 and python-docx for document parsing

### Frontend
- React.js with React Router for navigation
- Axios for API requests
- TailwindCSS for styling
- React Dropzone for file uploads
- React Hook Form for form handling
- React Hot Toast for notifications

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Node.js and npm (for local development)
- Python 3.9+ (for local development)

### Using Docker Compose (Recommended)

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-resume-analyzer.git
   cd ai-resume-analyzer
   ```

2. Start the services:
   ```
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/v1
   - API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Start MongoDB (either locally or using a cloud service)

5. Configure environment variables:
   ```
   export MONGO_URL=mongodb://localhost:27017
   export DB_NAME=resume_analyzer
   export DEBUG=True
   ```

6. Run the backend server:
   ```
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install the dependencies:
   ```
   npm install
   ```

3. Configure environment variables:
   ```
   echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env
   ```

4. Start the development server:
   ```
   npm start
   ```

5. Access the frontend at http://localhost:3000

## Usage

1. **Upload Resumes**: 
   - Navigate to the "Upload Resume" page
   - Drag and drop or select a PDF/DOCX file
   - Submit to parse the resume and extract information

2. **Create Job Descriptions**:
   - Go to the "Upload Job" page
   - Fill in the job details including title, company, and description
   - Submit to analyze and extract required skills

3. **View Matches**:
   - Job Matches: Click on a job from the "Jobs" page to view matching candidates
   - Resume Matches: Click on a resume from the "Resumes" page to view matching jobs

4. **Analyze Match Details**:
   - Click on "View Details" on any match to see an in-depth analysis
   - Review skill comparisons and compatibility scores

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 