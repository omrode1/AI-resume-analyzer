import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { resumeApi, jobApi, analysisApi } from '../services/api';
import { 
  DocumentTextIcon, 
  BriefcaseIcon,
  DocumentPlusIcon,
  DocumentDuplicateIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

function Dashboard() {
  const [stats, setStats] = useState({
    resumes: 0,
    jobs: 0,
    matches: 0
  });
  const [loading, setLoading] = useState(true);
  const [recentResumes, setRecentResumes] = useState([]);
  const [recentJobs, setRecentJobs] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch stats
        const [resumesRes, jobsRes, matchesRes] = await Promise.all([
          resumeApi.getAllResumes(),
          jobApi.getAllJobs(),
          analysisApi.getAllMatches()
        ]);
        
        setStats({
          resumes: resumesRes.data.length,
          jobs: jobsRes.data.length,
          matches: matchesRes.data.length
        });
        
        // Get 5 most recent resumes
        setRecentResumes(
          resumesRes.data
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 5)
        );
        
        // Get 5 most recent jobs
        setRecentJobs(
          jobsRes.data
            .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
            .slice(0, 5)
        );
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);
  
  const cards = [
    {
      name: 'Upload Resume',
      href: '/upload-resume',
      icon: DocumentPlusIcon,
      color: 'bg-primary-500',
      description: 'Upload and parse a candidate resume'
    },
    {
      name: 'Upload Job Description',
      href: '/upload-job',
      icon: DocumentDuplicateIcon,
      color: 'bg-secondary-500',
      description: 'Create a new job description'
    },
    {
      name: 'View Resumes',
      href: '/resumes',
      icon: DocumentTextIcon,
      color: 'bg-green-500',
      description: 'Browse and manage all resumes'
    },
    {
      name: 'View Jobs',
      href: '/jobs',
      icon: BriefcaseIcon,
      color: 'bg-purple-500',
      description: 'Browse and manage all job descriptions'
    }
  ];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-1 text-sm text-gray-600">
          Welcome to AI Resume Analyzer - analyze and match candidate resumes with job descriptions
        </p>
      </div>
      
      {/* Stats overview */}
      <div className="mt-4 grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-primary-100 rounded-md p-3">
                <DocumentTextIcon className="h-6 w-6 text-primary-600" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Resumes</dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {loading ? '...' : stats.resumes}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-4 py-4 sm:px-6">
            <Link to="/resumes" className="text-sm font-medium text-primary-600 hover:text-primary-500">
              View all resumes
              <span aria-hidden="true"> &rarr;</span>
            </Link>
          </div>
        </div>
        
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-secondary-100 rounded-md p-3">
                <BriefcaseIcon className="h-6 w-6 text-secondary-600" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Jobs</dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {loading ? '...' : stats.jobs}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-4 py-4 sm:px-6">
            <Link to="/jobs" className="text-sm font-medium text-secondary-600 hover:text-secondary-500">
              View all jobs
              <span aria-hidden="true"> &rarr;</span>
            </Link>
          </div>
        </div>
        
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-green-100 rounded-md p-3">
                <ChartBarIcon className="h-6 w-6 text-green-600" aria-hidden="true" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Matches</dt>
                  <dd>
                    <div className="text-lg font-medium text-gray-900">
                      {loading ? '...' : stats.matches}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 px-4 py-4 sm:px-6">
            <span className="text-sm font-medium text-gray-500">
              Resume-job matches
            </span>
          </div>
        </div>
      </div>
      
      {/* Quick action cards */}
      <div className="mt-8">
        <h2 className="text-lg font-medium text-gray-900">Quick Actions</h2>
        
        <div className="mt-4 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {cards.map((card) => (
            <div key={card.name} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className={`flex-shrink-0 rounded-md p-3 ${card.color}`}>
                    <card.icon className="h-6 w-6 text-white" aria-hidden="true" />
                  </div>
                  <div className="ml-5">
                    <h3 className="text-lg font-medium text-gray-900">{card.name}</h3>
                    <p className="mt-1 text-sm text-gray-500">{card.description}</p>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 px-5 py-3">
                <Link
                  to={card.href}
                  className="text-sm font-medium text-primary-600 hover:text-primary-500"
                >
                  Go <span aria-hidden="true">&rarr;</span>
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Recent items */}
      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent resumes */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
            <h3 className="text-lg font-medium leading-6 text-gray-900">Recent Resumes</h3>
          </div>
          {loading ? (
            <div className="py-10 text-center text-gray-500">Loading...</div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {recentResumes.length === 0 ? (
                <li className="py-4 px-6 text-center text-gray-500">No resumes uploaded yet</li>
              ) : (
                recentResumes.map((resume) => (
                  <li key={resume._id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                    <Link to={`/resume-matches/${resume._id}`} className="flex items-center">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-primary-600 truncate">{resume.candidate_name}</p>
                        <p className="text-sm text-gray-500 truncate">
                          {resume.skills.slice(0, 3).map(skill => skill.name).join(', ')}
                          {resume.skills.length > 3 && '...'}
                        </p>
                      </div>
                      <div className="ml-4 flex-shrink-0">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          {new Date(resume.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </Link>
                  </li>
                ))
              )}
            </ul>
          )}
          <div className="border-t border-gray-200 px-4 py-4 sm:px-6">
            <Link to="/resumes" className="text-sm font-medium text-primary-600 hover:text-primary-500">
              View all resumes <span aria-hidden="true">&rarr;</span>
            </Link>
          </div>
        </div>
        
        {/* Recent jobs */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 border-b border-gray-200 sm:px-6">
            <h3 className="text-lg font-medium leading-6 text-gray-900">Recent Jobs</h3>
          </div>
          {loading ? (
            <div className="py-10 text-center text-gray-500">Loading...</div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {recentJobs.length === 0 ? (
                <li className="py-4 px-6 text-center text-gray-500">No jobs added yet</li>
              ) : (
                recentJobs.map((job) => (
                  <li key={job._id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                    <Link to={`/job-matches/${job._id}`} className="flex items-center">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-secondary-600 truncate">{job.title}</p>
                        <p className="text-sm text-gray-500 truncate">
                          {job.company} {job.location && `• ${job.location}`}
                        </p>
                      </div>
                      <div className="ml-4 flex-shrink-0">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {job.job_type || 'Job'}
                        </span>
                      </div>
                    </Link>
                  </li>
                ))
              )}
            </ul>
          )}
          <div className="border-t border-gray-200 px-4 py-4 sm:px-6">
            <Link to="/jobs" className="text-sm font-medium text-secondary-600 hover:text-secondary-500">
              View all jobs <span aria-hidden="true">&rarr;</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 