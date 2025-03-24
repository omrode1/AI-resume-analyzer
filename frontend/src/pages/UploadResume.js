import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { DocumentArrowUpIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { resumeApi } from '../services/api';

function UploadResume() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles) => {
    // Only accept one file
    const selectedFile = acceptedFiles[0];
    
    // Check file type
    const fileType = selectedFile.type;
    if (fileType !== 'application/pdf' && fileType !== 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      toast.error('Please upload a PDF or DOCX file');
      return;
    }
    
    // Check file size (max 10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB');
      return;
    }
    
    // Set the file
    setFile(selectedFile);
  }, []);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1
  });
  
  const handleRemoveFile = () => {
    setFile(null);
  };
  
  const handleUpload = async () => {
    if (!file) {
      toast.error('Please select a file to upload');
      return;
    }
    
    setUploading(true);
    
    try {
      const response = await resumeApi.uploadResume(file);
      
      toast.success('Resume uploaded and parsed successfully');
      
      // Navigate to the resume details page
      navigate(`/resume-matches/${response.data._id}`);
    } catch (error) {
      console.error('Error uploading resume:', error);
      toast.error(error.response?.data?.detail || 'Error uploading resume');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Upload Resume</h1>
        <p className="mt-1 text-sm text-gray-600">
          Upload a resume to parse and analyze it
        </p>
      </div>
      
      <div className="bg-white shadow rounded-lg overflow-hidden">
        <div className="p-6">
          <div className="space-y-6">
            {/* File dropzone */}
            {!file && (
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer ${
                  isDragActive
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-500'
                }`}
              >
                <input {...getInputProps()} />
                <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm font-medium text-gray-900">
                  {isDragActive
                    ? 'Drop your resume here...'
                    : 'Drag and drop your resume, or click to browse'
                }
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  PDF or DOCX up to 10MB
                </p>
              </div>
            )}
            
            {/* Selected file */}
            {file && (
              <div className="rounded-lg border border-gray-300 bg-gray-50 p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center">
                    <DocumentArrowUpIcon className="h-8 w-8 text-primary-500 mr-3" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{file.name}</p>
                      <p className="text-xs text-gray-500">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={handleRemoveFile}
                    className="text-gray-400 hover:text-gray-500"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            )}
            
            {/* Upload button */}
            <div className="flex justify-end">
              <button
                type="button"
                onClick={handleUpload}
                disabled={!file || uploading}
                className={`rounded-md px-4 py-2 text-sm font-medium text-white shadow-sm ${
                  !file || uploading
                    ? 'bg-gray-300 cursor-not-allowed'
                    : 'bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500'
                }`}
              >
                {uploading ? 'Uploading...' : 'Upload Resume'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default UploadResume; 