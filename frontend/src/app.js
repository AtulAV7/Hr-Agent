import React, { useState, useEffect } from 'react';
import './App.css';
import JobDescriptionInput from './components/JobDescriptionInput';
import ResumeUpload from './components/ResumeUpload';
import CandidatePanel from './components/CandidatePanel';
import InterviewScheduler from './components/InterviewScheduler';
import apiService from './services/api';

function App() {
  const [currentStep, setCurrentStep] = useState('job-description');
  const [jobCreated, setJobCreated] = useState(false);
  const [candidates, setCandidates] = useState([]);
  const [scheduledInterviews, setScheduledInterviews] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [jobData, setJobData] = useState(null);

  // Check API health on component mount
  useEffect(() => {
    const checkApiHealth = async () => {
      try {
        await apiService.healthCheck();
        console.log('API is healthy');
      } catch (error) {
        console.warn('API health check failed:', error);
        setError('Unable to connect to the server. Please check if the backend is running.');
      }
    };

    checkApiHealth();
  }, []);

  const handleJobSubmit = async (jobFormData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.createJobDescription(jobFormData);
      console.log('Job created:', response.data);
      
      setJobData(jobFormData);
      setJobCreated(true);
      setCurrentStep('resume-upload');
      
      // Show success message
      setTimeout(() => {
        alert('Job description created successfully! You can now upload resumes.');
      }, 500);
      
    } catch (error) {
      console.error('Error creating job:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to create job description. Please try again.';
      setError(errorMessage);
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleResumesUpload = async (formData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.uploadResumes(formData);
      console.log('Resumes uploaded:', response.data);
      
      setCandidates(response.data.candidates);
      setCurrentStep('candidate-review');
      
      // Show success message
      setTimeout(() => {
        alert(`Successfully processed ${response.data.candidates.length} resumes!`);
      }, 500);
      
    } catch (error) {
      console.error('Error uploading resumes:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to upload resumes. Please try again.';
      setError(errorMessage);
      alert(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCandidates = async (selectedCandidateIds) => {
    if (selectedCandidateIds.length === 0) {
      alert('Please select at least one candidate.');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.scheduleInterviews(selectedCandidateIds);
      console.log('Interviews scheduled:', response.data);
      
      setScheduledInterviews(response.data.interviews);
      setCurrentStep('interview-results');
      
      // Show success message
      setTimeout(() => {
        alert(`Successfully scheduled ${response.data.interviews.length} interviews!`);
      }, 500);
      
    } catch (error) {
      console.error('Error scheduling interviews:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to schedule interviews. Please try again.';
      setError(errorMessage);
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToSelection = () => {
    setCurrentStep('candidate-review');
    setError(null);
  };

  const resetWorkflow = () => {
    if (window.confirm('Are you sure you want to start a new workflow? This will clear all current data.')) {
      setCurrentStep('job-description');
      setJobCreated(false);
      setCandidates([]);
      setScheduledInterviews([]);
      setJobData(null);
      setError(null);
    }
  };

  const getStepStatus = (step) => {
    switch (step) {
      case 'job-description':
        return currentStep === 'job-description' ? 'active' : jobCreated ? 'completed' : '';
      case 'resume-upload':
        return currentStep === 'resume-upload' ? 'active' : candidates.length > 0 ? 'completed' : '';
      case 'candidate-review':
        return currentStep === 'candidate-review' ? 'active' : scheduledInterviews.length > 0 ? 'completed' : '';
      case 'interview-results':
        return currentStep === 'interview-results' ? 'active' : '';
      default:
        return '';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 HR AI Agent</h1>
        <p>Automated Resume Screening and Interview Scheduling