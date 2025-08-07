import React, { useState } from 'react';

const JobDescriptionInput = ({ onJobSubmit }) => {
  const [jobData, setJobData] = useState({
    title: '',
    description: '',
    requirements: '',
    location: '',
    department: ''
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setJobData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onJobSubmit(jobData);
  };

  return (
    <div className="job-description-input">
      <h2>Job Description</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Job Title:</label>
          <input
            type="text"
            name="title"
            value={jobData.title}
            onChange={handleInputChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Description:</label>
          <textarea
            name="description"
            value={jobData.description}
            onChange={handleInputChange}
            rows="4"
            required
          />
        </div>
        
        <div className="form-group">
          <label>Requirements:</label>
          <textarea
            name="requirements"
            value={jobData.requirements}
            onChange={handleInputChange}
            rows="4"
            required
          />
        </div>
        
        <div className="form-group">
          <label>Location:</label>
          <input
            type="text"
            name="location"
            value={jobData.location}
            onChange={handleInputChange}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Department:</label>
          <input
            type="text"
            name="department"
            value={jobData.department}
            onChange={handleInputChange}
            required
          />
        </div>
        
        <button type="submit">Create Job Description</button>
      </form>
    </div>
  );
};

export default JobDescriptionInput;