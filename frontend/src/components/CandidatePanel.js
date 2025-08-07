import React, { useState } from 'react';

const CandidatePanel = ({ candidates, onSelectCandidates }) => {
  const [selectedCandidates, setSelectedCandidates] = useState(new Set());

  const toggleCandidateSelection = (candidateId) => {
    setSelectedCandidates(prev => {
      const newSet = new Set(prev);
      if (newSet.has(candidateId)) {
        newSet.delete(candidateId);
      } else {
        newSet.add(candidateId);
      }
      return newSet;
    });
  };

  const selectAllCandidates = () => {
    if (selectedCandidates.size === candidates.length) {
      // Deselect all
      setSelectedCandidates(new Set());
    } else {
      // Select all
      setSelectedCandidates(new Set(candidates.map(c => c.candidate_id)));
    }
  };

  const handleProceedToScheduling = () => {
    if (selectedCandidates.size === 0) {
      alert('Please select at least one candidate to proceed.');
      return;
    }
    
    onSelectCandidates(Array.from(selectedCandidates));
  };

  const getScoreColor = (score) => {
    if (score >= 90) return '#4CAF50'; // Green
    if (score >= 80) return '#FF9800'; // Orange
    if (score >= 70) return '#2196F3'; // Blue
    if (score >= 60) return '#9C27B0'; // Purple
    return '#F44336'; // Red
  };

  const getScoreLabel = (score) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Poor';
  };

  const getRankSuffix = (rank) => {
    if (rank % 10 === 1 && rank % 100 !== 11) return 'st';
    if (rank % 10 === 2 && rank % 100 !== 12) return 'nd';
    if (rank % 10 === 3 && rank % 100 !== 13) return 'rd';
    return 'th';
  };

  return (
    <div className="candidate-panel">
      <div className="panel-header">
        <h2>👥 Candidate Rankings</h2>
        <div className="panel-actions">
          <button 
            onClick={selectAllCandidates}
            className="select-all-btn"
          >
            {selectedCandidates.size === candidates.length ? '❌ Deselect All' : '✅ Select All'}
          </button>
          <button 
            onClick={handleProceedToScheduling}
            className="proceed-btn"
            disabled={selectedCandidates.size === 0}
          >
            📅 Schedule Interviews ({selectedCandidates.size})
          </button>
        </div>
      </div>

      {candidates.length === 0 ? (
        <div className="no-candidates">
          <p>No candidates to display. Please upload resume files first.</p>
        </div>
      ) : (
        <div className="candidates-list">
          {candidates.map((candidate, index) => (
            <div 
              key={candidate.candidate_id}
              className={`candidate-card ${selectedCandidates.has(candidate.candidate_id) ? 'selected' : ''}`}
              onClick={() => toggleCandidateSelection(candidate.candidate_id)}
            >
              <div className="candidate-header">
                <div className="candidate-info">
                  <input 
                    type="checkbox"
                    checked={selectedCandidates.has(candidate.candidate_id)}
                    onChange={() => toggleCandidateSelection(candidate.candidate_id)}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <div>
                    <h3>{candidate.name}</h3>
                    <div className="candidate-email">{candidate.email}</div>
                    {candidate.phone && (
                      <div className="candidate-phone">{candidate.phone}</div>
                    )}
                  </div>
                </div>
                <div className="candidate-score">
                  <div 
                    className="score-badge"
                    style={{ backgroundColor: getScoreColor(candidate.score) }}
                  >
                    {Math.round(candidate.score)}
                  </div>
                  <div className="rank">
                    {index + 1}{getRankSuffix(index + 1)} Place
                  </div>
                </div>
              </div>

              <div className="candidate-details">
                <div className="summary">
                  <h4>📋 Summary</h4>
                  <p>{candidate.summary}</p>
                </div>

                <div className="skills">
                  <h4>🛠️ Matching Skills</h4>
                  <div className="skills-tags">
                    {candidate.skills_match && candidate.skills_match.length > 0 ? (
                      candidate.skills_match.map((skill, skillIndex) => (
                        <span key={skillIndex} className="skill-tag">
                          {skill}
                        </span>
                      ))
                    ) : (
                      <span style={{ color: '#666', fontStyle: 'italic' }}>
                        No specific skills listed
                      </span>
                    )}
                  </div>
                </div>

                {candidate.experience_years !== null && candidate.experience_years !== undefined && (
                  <div className="experience">
                    <h4>💼 Experience</h4>
                    <p>
                      {candidate.experience_years > 0 
                        ? `${candidate.experience_years} year${candidate.experience_years > 1 ? 's' : ''} of experience`
                        : 'Entry level / Fresh graduate'
                      }
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {candidates.length > 0 && (
        <div style={{ marginTop: '2rem', padding: '1.5rem', background: '#f8f9fa', borderRadius: '8px' }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>📊 Selection Summary</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
                {candidates.length}
              </div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Total Candidates</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#4CAF50' }}>
                {selectedCandidates.size}
              </div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>Selected for Interview</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#FF9800' }}>
                {candidates.filter(c => c.score >= 80).length}
              </div>
              <div style={{ fontSize: '0.9rem', color: '#666' }}>High Scoring (80+)</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CandidatePanel;