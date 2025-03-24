import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { 
  ArrowLeftIcon,
  ChartBarIcon, 
  DocumentTextIcon,
  BriefcaseIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';
import { analysisApi } from '../services/api';

function AnalysisResult() {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMatchData = async () => {
      try {
        setLoading(true);
        const response = await analysisApi.getMatchById(matchId);
        setMatch(response.data);
      } catch (error) {
        console.error('Error fetching match data:', error);
        toast.error('Failed to load match details');
      } finally {
        setLoading(false);
      }
    };

    fetchMatchData();
  }, [matchId]);

  // Helper to render color based on score
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Helper to get background color based on score
  const getScoreBgClass = (score) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

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
          <p className="mt-2 text-gray-500">Loading match analysis...</p>
        </div>
      ) : (
        <>
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-900">Match Analysis</h1>
            <p className="mt-1 text-sm text-gray-600">
              Detailed analysis between {match?.resume?.candidate_name || 'Candidate'} and {match?.job?.title || 'Job'}
            </p>
          </div>

          {/* Overall match score card */}
          <div className="mb-8 bg-white shadow rounded-lg overflow-hidden">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex flex-col items-center">
                <h3 className="text-lg font-medium text-gray-900">Overall Match Score</h3>
                <div
                  className={`mt-4 flex items-center justify-center h-32 w-32 rounded-full ${getScoreBgClass(
                    match?.match_score
                  )}`}
                >
                  <span className={`text-4xl font-bold ${getScoreColor(match?.match_score)}`}>
                    {match?.match_score.toFixed(1)}%
                  </span>
                </div>
                <p className="mt-2 text-sm text-gray-500">
                  {match?.match_score >= 80
                    ? 'Excellent match! This candidate is highly suitable for the job.'
                    : match?.match_score >= 60
                    ? 'Good match. This candidate meets many of the job requirements.'
                    : 'This candidate may need additional training or experience for this role.'}
                </p>
              </div>
            </div>
          </div>

          {/* Match details grid */}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 mb-8">
            {/* Candidate information */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:px-6 bg-gray-50 flex items-center">
                <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-2" />
                <h3 className="text-lg font-medium leading-6 text-gray-900">Candidate Details</h3>
              </div>
              <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-500">Name</h4>
                  <p className="mt-1 text-sm text-gray-900">{match?.resume?.candidate_name || 'N/A'}</p>
                </div>
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-500">Email</h4>
                  <p className="mt-1 text-sm text-gray-900">{match?.resume?.email || 'N/A'}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Skills</h4>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {match?.resume?.skills && match.resume.skills.length > 0 ? (
                      match.resume.skills.map((skill, index) => (
                        <span
                          key={index}
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            match.matched_skills.some(
                              (s) => s.name.toLowerCase() === skill.name.toLowerCase()
                            )
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {skill.name}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-gray-500">No skills found</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Job information */}
            <div className="bg-white shadow rounded-lg overflow-hidden">
              <div className="px-4 py-5 sm:px-6 bg-gray-50 flex items-center">
                <BriefcaseIcon className="h-5 w-5 text-gray-400 mr-2" />
                <h3 className="text-lg font-medium leading-6 text-gray-900">Job Details</h3>
              </div>
              <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-500">Job Title</h4>
                  <p className="mt-1 text-sm text-gray-900">{match?.job?.title || 'N/A'}</p>
                </div>
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-500">Company</h4>
                  <p className="mt-1 text-sm text-gray-900">{match?.job?.company_name || 'N/A'}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">Required Skills</h4>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {match?.job?.required_skills && match.job.required_skills.length > 0 ? (
                      match.job.required_skills.map((skill, index) => (
                        <span
                          key={index}
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            match.matched_skills.some(
                              (s) => s.name.toLowerCase() === skill.name.toLowerCase()
                            )
                              ? 'bg-green-100 text-green-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {skill.name}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-gray-500">No skills specified</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Skills comparison table */}
          <div className="bg-white shadow rounded-lg overflow-hidden mb-8">
            <div className="px-4 py-5 sm:px-6 bg-gray-50 flex items-center">
              <ChartBarIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-lg font-medium leading-6 text-gray-900">Skills Comparison</h3>
            </div>
            <div className="border-t border-gray-200">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Required Skill
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Match Status
                      </th>
                      <th
                        scope="col"
                        className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                      >
                        Candidate Experience
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {match?.job?.required_skills && match.job.required_skills.length > 0 ? (
                      match.job.required_skills.map((skill, index) => {
                        const isMatched = match.matched_skills.some(
                          (s) => s.name.toLowerCase() === skill.name.toLowerCase()
                        );
                        const candidateSkill = match.resume.skills.find(
                          (s) => s.name.toLowerCase() === skill.name.toLowerCase()
                        );

                        return (
                          <tr key={index} className={isMatched ? 'bg-green-50' : ''}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {skill.name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {isMatched ? (
                                <span className="inline-flex items-center text-green-600">
                                  <CheckCircleIcon className="h-5 w-5 mr-1" />
                                  Matched
                                </span>
                              ) : (
                                <span className="inline-flex items-center text-red-600">
                                  <XCircleIcon className="h-5 w-5 mr-1" />
                                  Not Matched
                                </span>
                              )}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {candidateSkill ? (
                                <span>
                                  {candidateSkill.years_of_experience
                                    ? `${candidateSkill.years_of_experience} years`
                                    : 'Experience level not specified'}
                                </span>
                              ) : (
                                'Not mentioned in resume'
                              )}
                            </td>
                          </tr>
                        );
                      })
                    ) : (
                      <tr>
                        <td colSpan="3" className="px-6 py-4 text-center text-sm text-gray-500">
                          No required skills specified for this job
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Match analysis summary */}
          <div className="bg-white shadow rounded-lg overflow-hidden mb-8">
            <div className="px-4 py-5 sm:px-6 bg-gray-50">
              <h3 className="text-lg font-medium leading-6 text-gray-900">Analysis Summary</h3>
            </div>
            <div className="border-t border-gray-200 px-4 py-5 sm:p-6">
              <div className="prose">
                <p className="text-gray-700">
                  {match?.resume?.candidate_name || 'The candidate'} matches{' '}
                  {match?.matched_skills?.length || 0} out of {match?.job?.required_skills?.length || 0}{' '}
                  required skills for the {match?.job?.title || 'job position'}.
                </p>
                
                {match?.match_score >= 80 ? (
                  <>
                    <p className="text-green-700 font-medium mt-4">
                      This is an excellent match! The candidate has most of the skills required for this position.
                    </p>
                    <p className="text-gray-700 mt-2">
                      The candidate's experience and skillset align well with the job requirements.
                      They would likely require minimal training to be effective in this role.
                    </p>
                  </>
                ) : match?.match_score >= 60 ? (
                  <>
                    <p className="text-yellow-700 font-medium mt-4">
                      This is a good match. The candidate has many of the required skills but may need some additional training.
                    </p>
                    <p className="text-gray-700 mt-2">
                      With some additional training or experience in{' '}
                      {match?.job?.required_skills
                        .filter(
                          (skill) =>
                            !match.matched_skills.some(
                              (s) => s.name.toLowerCase() === skill.name.toLowerCase()
                            )
                        )
                        .slice(0, 2)
                        .map((skill) => skill.name)
                        .join(', ')}{' '}
                      {match?.job?.required_skills.filter(
                        (skill) =>
                          !match.matched_skills.some(
                            (s) => s.name.toLowerCase() === skill.name.toLowerCase()
                          )
                      ).length > 2
                        ? 'and other areas'
                        : ''}
                      , the candidate could become more effective in this role.
                    </p>
                  </>
                ) : (
                  <>
                    <p className="text-red-700 font-medium mt-4">
                      This candidate may not be the best fit for this position based on skills match.
                    </p>
                    <p className="text-gray-700 mt-2">
                      The candidate is missing several key skills required for this role, including{' '}
                      {match?.job?.required_skills
                        .filter(
                          (skill) =>
                            !match.matched_skills.some(
                              (s) => s.name.toLowerCase() === skill.name.toLowerCase()
                            )
                        )
                        .slice(0, 3)
                        .map((skill) => skill.name)
                        .join(', ')}
                      {match?.job?.required_skills.filter(
                        (skill) =>
                          !match.matched_skills.some(
                            (s) => s.name.toLowerCase() === skill.name.toLowerCase()
                          )
                      ).length > 3
                        ? ' and others'
                        : ''}
                      . Significant training would be required.
                    </p>
                  </>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default AnalysisResult; 