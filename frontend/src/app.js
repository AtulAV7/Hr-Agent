import React, { useState, useEffect } from 'react';
import './App.css';
import JobDescriptionInput from './components/JobDescriptionInput';
import ResumeUpload from './components/ResumeUpload';
import CandidatePanel from './components/CandidatePanel';
import InterviewScheduler from './components/InterviewScheduler';
import apiService from './services/api';

function App() {
  // State management
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

  // Handle job description submission
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
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          'Failed to create job description. Please try again.';
      setError(errorMessage);
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Handle resume upload
  const handleResumesUpload = async (formData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.uploadResumes(formData);
      console.log('Resumes uploaded:', response.data);
      
      setCandidates(response.data.candidates || response.data);
      setCurrentStep('candidate-review');
      
      // Show success message
      const candidateCount = response.data.candidates?.length || response.data.length || 0;
      setTimeout(() => {
        alert(`Successfully processed ${candidateCount} resumes!`);
      }, 500);
      
    } catch (error) {
      console.error('Error uploading resumes:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          'Failed to upload resumes. Please try again.';
      setError(errorMessage);
      alert(errorMessage);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Handle candidate selection for interviews
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
      
      setScheduledInterviews(response.data.interviews || response.data);
      setCurrentStep('interview-results');
      
      // Show success message
      const interviewCount = response.data.interviews?.length || response.data.length || 0;
      setTimeout(() => {
        alert(`Successfully scheduled ${interviewCount} interviews!`);
      }, 500);
      
    } catch (error) {
      console.error('Error scheduling interviews:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.response?.data?.message || 
                          'Failed to schedule interviews. Please try again.';
      setError(errorMessage);
      alert(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Navigate back to candidate selection
  const handleBackToSelection = () => {
    setCurrentStep('candidate-review');
    setError(null);
  };

  // Reset entire workflow
  const resetWorkflow = () => {
    if (window.confirm('Are you sure you want to start a new workflow? This will clear all current data.')) {
      setCurrentStep('job-description');
      setJobCreated(false);
      setCandidates([]);
      setScheduledInterviews([]);
      setJobData(null);
      setError(null);
      setLoading(false);
    }
  };

  // Get step status for navigation
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

  // Calculate statistics
  const getStats = () => {
    const totalCandidates = candidates.length;
    const totalInterviews = scheduledInterviews.length;
    const topCandidates = candidates.filter(c => (c.score || 0) >= 80).length;
    
    return {
      totalCandidates,
      totalInterviews,
      topCandidates
    };
  };

  const stats = getStats();

  return (
    <div className="App">
      {/* Header Section */}
      <header className="App-header">
        <h1>🤖 HR AI Agent</h1>
        <p>Automated Resume Screening and Interview Scheduling</p>
        {jobData && (
          <div className="current-job-info">
            <span>Current Job: <strong>{jobData.title}</strong> - {jobData.department}</span>
          </div>
        )}
      </header>

      {/* Workflow Navigation */}
      <nav className="workflow-nav">
        <div className={`nav-step ${getStepStatus('job-description')}`}>
          <span className="step-number">1</span>
          <span className="step-title">Job Description</span>
        </div>
        <div className="nav-connector"></div>
        <div className={`nav-step ${getStepStatus('resume-upload')}`}>
          <span className="step-number">2</span>
          <span className="step-title">Upload Resumes</span>
        </div>
        <div className="nav-connector"></div>
        <div className={`nav-step ${getStepStatus('candidate-review')}`}>
          <span className="step-number">3</span>
          <span className="step-title">Review Candidates</span>
        </div>
        <div className="nav-connector"></div>
        <div className={`nav-step ${getStepStatus('interview-results')}`}>
          <span className="step-number">4</span>
          <span className="step-title">Interview Results</span>
        </div>
      </nav>

      {/* Main Content */}
      <main className="App-main">
        {/* Loading Overlay */}
        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner"></div>
            <p>Processing... Please wait</p>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span>{error}</span>
            <button 
              onClick={() => setError(null)} 
              className="error-close"
              aria-label="Close error message"
            >
              ×
            </button>
          </div>
        )}

        {/* Step Components */}
        {currentStep === 'job-description' && (
          <JobDescriptionInput 
            onJobSubmit={handleJobSubmit} 
            disabled={loading}
          />
        )}

        {currentStep === 'resume-upload' && (
          <ResumeUpload 
            onResumesUpload={handleResumesUpload}
            disabled={loading}
          />
        )}

        {currentStep === 'candidate-review' && (
          <CandidatePanel 
            candidates={candidates}
            onSelectCandidates={handleSelectCandidates}
            disabled={loading}
          />
        )}

        {currentStep === 'interview-results' && (
          <InterviewScheduler 
            scheduledInterviews={scheduledInterviews}
            onBackToSelection={handleBackToSelection}
            disabled={loading}
          />
        )}

        {/* Stats Summary */}
        {(stats.totalCandidates > 0 || stats.totalInterviews > 0) && (
          <div className="stats-summary">
            <div className="stat-item">
              <span className="stat-number">{stats.totalCandidates}</span>
              <span className="stat-label">Candidates Processed</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{stats.totalInterviews}</span>
              <span className="stat-label">Interviews Scheduled</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{stats.topCandidates}</span>
              <span className="stat-label">Top Candidates (80+)</span>
            </div>
          </div>
        )}
      </main>

      {/* Footer Section */}
      <footer className="App-footer">
        <div className="footer-content">
          <button 
            onClick={resetWorkflow} 
            className="reset-btn"
            disabled={loading}
          >
            🔄 Start New Workflow
          </button>
        </div>
      </footer>
    </div>
  );
}

export default App;