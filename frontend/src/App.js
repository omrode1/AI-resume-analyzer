import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import UploadResume from './pages/UploadResume';
import UploadJob from './pages/UploadJob';
import Resumes from './pages/Resumes';
import Jobs from './pages/Jobs';
import JobMatches from './pages/JobMatches';
import ResumeMatches from './pages/ResumeMatches';
import AnalysisResult from './pages/AnalysisResult';
import Layout from './components/Layout';
import './App.css';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/upload-resume" element={<UploadResume />} />
        <Route path="/upload-job" element={<UploadJob />} />
        <Route path="/resumes" element={<Resumes />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/job-matches/:jobId" element={<JobMatches />} />
        <Route path="/resume-matches/:resumeId" element={<ResumeMatches />} />
        <Route path="/analysis/:matchId" element={<AnalysisResult />} />
      </Routes>
    </Layout>
  );
}

export default App; 