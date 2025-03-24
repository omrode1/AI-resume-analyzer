import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { 
  UserIcon, 
  ArrowLeftIcon,
  DocumentTextIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { jobApi, analysisApi } from '../services/api';

function JobMatches() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Get job details
        const jobResponse = await jobApi.getJobById(jobId);
        setJob(jobResponse.data);
        
        // Get matches for this job
        const matchesResponse = await analysisApi.getTopCandidates(jobId, 50);
        setMatches(matchesResponse.data);
      } catch (error) {
        console.error('Error fetching job data:', error);
        toast.error('Failed to load job details or matches');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [jobId]);

  return (
    <div>
      <div className="mb-6">
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700"
        >
          <ArrowLeftIcon className="mr-1 h-4 w-4" aria-hidden="true" />
          Back
        </button>
      </div>

      <div className="mb-6 sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {loading ? 'Loading...' : `Top Candidates for ${job?.title || 'Job'}`}
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            {loading
              ? 'Loading job details...'
              : `${matches.length} candidates sorted by match score`}
          </p>
        </div>
      </div>

      {loading ? (
        <div className="p-10 text-center bg-white shadow rounded-lg">
          <svg
            className="mx-auto h-12 w-12 animate-spin text-gray-400"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <p className="mt-2 text-gray-500">Loading match results...</p>
        </div>
      ) : (
        <>
          {/* Job details card */}
          <div className="mb-6 bg-white shadow rounded-lg overflow-hidden">
            <div className="px-4 py-5 sm:px-6 bg-gray-50">
              <h3 className="text-lg font-medium leading-6 text-gray-900">Job Details</h3>
            </div>
            <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
              <dl className="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2">
                <div className="sm:col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Job Title</dt>
                  <dd className="mt-1 text-sm text-gray-900">{job?.title || 'N/A'}</dd>
                </div>
                <div className="sm:col-span-1">
                  <dt className="text-sm font-medium text-gray-500">Company</dt>
                  <dd className="mt-1 text-sm text-gray-900">{job?.company_name || 'N/A'}</dd>
                </div>
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500">Required Skills</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {job?.required_skills && job.required_skills.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {job.required_skills.map((skill, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary-100 text-secondary-800"
                          >
                            {skill.name}
                          </span>
                        ))}
                      </div>
                    ) : (
                      'No skills specified'
                    )}
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          {/* Matches list */}
          <div className="bg-white shadow rounded-lg overflow-hidden">
            {matches.length === 0 ? (
              <div className="p-10 text-center">
                <UserIcon className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-semibold text-gray-900">No matches found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  No candidates match this job description yet.
                </p>
                <div className="mt-6">
                  <Link
                    to="/upload-resume"
                    className="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600"
                  >
                    <DocumentTextIcon className="-ml-0.5 mr-1.5 h-5 w-5" aria-hidden="true" />
                    Upload Resume
                  </Link>
                </div>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Rank
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Candidate
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Match Score
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Skills Match
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {matches.map((match, index) => (
                      <tr key={match._id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          #{index + 1}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center bg-primary-100 rounded-full">
                              <span className="text-primary-700 font-medium">
                                {match.resume?.candidate_name
                                  ?.split(' ')
                                  .map((n) => n[0])
                                  .slice(0, 2)
                                  .join('') || 'NA'}
                              </span>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">
                                {match.resume?.candidate_name || 'Unknown'}
                              </div>
                              <div className="text-sm text-gray-500">
                                {match.resume?.email || 'No email provided'}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                match.match_score >= 80
                                  ? 'bg-green-100 text-green-800'
                                  : match.match_score >= 60
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-red-100 text-red-800'
                              }`}
                            >
                              {match.match_score.toFixed(1)}%
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {match.matched_skills?.length || 0} of{' '}
                            {job?.required_skills?.length || 0} skills
                          </div>
                          <div className="text-xs text-gray-500">
                            {match.matched_skills?.length > 0
                              ? match.matched_skills
                                  .slice(0, 2)
                                  .map((skill) => skill.name)
                                  .join(', ')
                              : 'No matching skills'}
                            {match.matched_skills?.length > 2 && ' ...'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <Link
                            to={`/analysis/${match._id}`}
                            className="text-primary-600 hover:text-primary-900"
                          >
                            <span className="inline-flex items-center">
                              <EyeIcon className="mr-1 h-4 w-4" />
                              View Details
                            </span>
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default JobMatches; 