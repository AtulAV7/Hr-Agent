import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Job Description
  createJobDescription: (jobData) => api.post('/job-description', jobData),
  
  // Resume Upload
  uploadResumes: (formData) => api.post('/upload-resumes', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }),
  
  // Candidates
  getCandidates: () => api.get('/candidates'),
  
  // Interview Scheduling
  scheduleInterviews: (candidateIds) => api.post('/schedule-interviews', candidateIds),
  
  // Health Check
  healthCheck: () => api.get('/health'),
};

export default apiService;