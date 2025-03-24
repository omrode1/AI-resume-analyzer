import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { jobApi } from '../services/api';

function UploadJob() {
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      title: '',
      company: '',
      text: '',
    },
  });
  
  const onSubmit = async (data) => {
    setSubmitting(true);
    
    try {
      const response = await jobApi.createJob(data);
      
      toast.success('Job description created successfully');
      
      // Navigate to the job details page
      navigate(`/job-matches/${response.data._id}`);
    } catch (error) {
      console.error('Error creating job description:', error);
      toast.error(error.response?.data?.detail || 'Error creating job description');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Create Job Description</h1>
        <p className="mt-1 text-sm text-gray-600">
          Enter job details to create and parse a job description
        </p>
      </div>
      
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Job title */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                Job Title
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="title"
                  className={`block w-full rounded-md border ${
                    errors.title ? 'border-red-300' : 'border-gray-300'
                  } shadow-sm p-2 focus:border-primary-500 focus:ring-primary-500 sm:text-sm`}
                  placeholder="e.g., Senior Software Engineer"
                  {...register('title', { required: 'Job title is required' })}
                />
              </div>
              {errors.title && (
                <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
              )}
            </div>
            
            {/* Company name */}
            <div>
              <label htmlFor="company" className="block text-sm font-medium text-gray-700">
                Company Name
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  id="company"
                  className={`block w-full rounded-md border ${
                    errors.company ? 'border-red-300' : 'border-gray-300'
                  } shadow-sm p-2 focus:border-primary-500 focus:ring-primary-500 sm:text-sm`}
                  placeholder="e.g., Acme Inc."
                  {...register('company', { required: 'Company name is required' })}
                />
              </div>
              {errors.company && (
                <p className="mt-1 text-sm text-red-600">{errors.company.message}</p>
              )}
            </div>
            
            {/* Job description text */}
            <div>
              <label htmlFor="text" className="block text-sm font-medium text-gray-700">
                Job Description
              </label>
              <div className="mt-1">
                <textarea
                  id="text"
                  rows={15}
                  className={`block w-full rounded-md border ${
                    errors.text ? 'border-red-300' : 'border-gray-300'
                  } shadow-sm p-2 focus:border-primary-500 focus:ring-primary-500 sm:text-sm`}
                  placeholder="Paste the full job description here..."
                  {...register('text', {
                    required: 'Job description is required',
                    minLength: {
                      value: 100,
                      message: 'Job description should be at least 100 characters',
                    },
                  })}
                />
              </div>
              {errors.text && (
                <p className="mt-1 text-sm text-red-600">{errors.text.message}</p>
              )}
              <p className="mt-1 text-xs text-gray-500">
                Paste the complete job description text. The system will automatically extract
                skills, requirements, and other details.
              </p>
            </div>
            
            {/* Submit button */}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={submitting}
                className={`rounded-md px-4 py-2 text-sm font-medium text-white shadow-sm ${
                  submitting
                    ? 'bg-gray-300 cursor-not-allowed'
                    : 'bg-secondary-600 hover:bg-secondary-700 focus:outline-none focus:ring-2 focus:ring-secondary-500'
                }`}
              >
                {submitting ? 'Creating...' : 'Create Job Description'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default UploadJob; 