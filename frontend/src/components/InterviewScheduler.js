import React, { useState } from 'react';

const InterviewScheduler = ({ scheduledInterviews, onBackToSelection }) => {
  const [expandedInterviews, setExpandedInterviews] = useState(new Set());

  const toggleInterviewDetails = (index) => {
    setExpandedInterviews(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const formatDateTime = (dateTimeString) => {
    try {
      const date = new Date(dateTimeString);
      return {
        date: date.toLocaleDateString('en-US', { 
          weekday: 'long', 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        }),
        time: date.toLocaleTimeString('en-US', { 
          hour: '2-digit', 
          minute: '2-digit',
          hour12: true 
        })
      };
    } catch (error) {
      return { date: 'Invalid Date', time: 'Invalid Time' };
    }
  };

  const getStatusColor = (status) => {
    switch (status.toLowerCase()) {
      case 'scheduled':
      case 'sent':
        return '#4CAF50';
      case 'failed':
        return '#F44336';
      case 'pending':
        return '#FF9800';
      default:
        return '#9E9E9E';
    }
  };

  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'scheduled':
        return '✅';
      case 'sent':
        return '📧';
      case 'failed':
        return '❌';
      case 'pending':
        return '⏳';
      default:
        return '❓';
    }
  };

  const calculateStats = () => {
    const total = scheduledInterviews.length;
    const successful = scheduledInterviews.filter(interview => 
      interview.calendar_status === 'scheduled' && interview.email_status === 'sent'
    ).length;
    const calendarSuccess = scheduledInterviews.filter(interview => 
      interview.calendar_status === 'scheduled'
    ).length;
    const emailSuccess = scheduledInterviews.filter(interview => 
      interview.email_status === 'sent'
    ).length;

    return { total, successful, calendarSuccess, emailSuccess };
  };

  const stats = calculateStats();

  return (
    <div className="interview-scheduler">
      <div className="scheduler-header">
        <h2>📅 Interview Scheduling Results</h2>
        <button onClick={onBackToSelection} className="back-btn">
          ← Back to Selection
        </button>
      </div>

      <div className="summary">
        <h3>📊 Scheduling Summary</h3>
        <p>
          Successfully scheduled <strong>{stats.successful}</strong> out of <strong>{stats.total}</strong> interviews.
          Calendar events: <strong>{stats.calendarSuccess}/{stats.total}</strong>, 
          Email confirmations: <strong>{stats.emailSuccess}/{stats.total}</strong>
        </p>
      </div>

      {scheduledInterviews.length === 0 ? (
        <div className="no-interviews">
          <p>No interviews have been scheduled yet.</p>
        </div>
      ) : (
        <div className="interviews-list">
          {scheduledInterviews.map((interview, index) => {
            const isExpanded = expandedInterviews.has(index);
            const dateTime = formatDateTime(interview.interview_time);

            return (
              <div key={index} className="interview-card">
                <div 
                  className="interview-header"
                  onClick={() => toggleInterviewDetails(index)}
                >
                  <div className="interview-info">
                    <h3>{interview.candidate}</h3>
                    <div className="interview-email">{interview.email}</div>
                    <div className="interview-time">
                      {dateTime.date} at {dateTime.time}
                    </div>
                  </div>
                  <div className="interview-status">
                    <div 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(interview.calendar_status) }}
                    >
                      {getStatusIcon(interview.calendar_status)} Calendar: {interview.calendar_status}
                    </div>
                    <div 
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(interview.email_status) }}
                    >
                      {getStatusIcon(interview.email_status)} Email: {interview.email_status}
                    </div>
                    <span className="toggle-icon">
                      {isExpanded ? '▼' : '▶'}
                    </span>
                  </div>
                </div>

                {isExpanded && (
                  <div className="interview-details">
                    <div className="detail-item">
                      <strong>Candidate:</strong>
                      <span>{interview.candidate}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Email:</strong>
                      <span>{interview.email}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Interview Date:</strong>
                      <span>{dateTime.date}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Interview Time:</strong>
                      <span>{dateTime.time}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Calendar Status:</strong>
                      <span className={`status ${interview.calendar_status}`}>
                        {getStatusIcon(interview.calendar_status)} {interview.calendar_status}
                      </span>
                    </div>
                    <div className="detail-item">
                      <strong>Email Status:</strong>
                      <span className={`status ${interview.email_status}`}>
                        {getStatusIcon(interview.email_status)} {interview.email_status}
                      </span>
                    </div>
                    {interview.meet_link && interview.meet_link !== 'No meet link' && interview.meet_link !== 'Authentication required' && (
                      <div className="detail-item">
                        <strong>Meeting Link:</strong>
                        <a 
                          href={interview.meet_link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                        >
                          {interview.meet_link}
                        </a>
                      </div>
                    )}
                    {interview.meet_link === 'Authentication required' && (
                      <div className="detail-item">
                        <strong>Meeting Link:</strong>
                        <span style={{ color: '#FF9800' }}>
                          📝 Google Calendar authentication required for meet links
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Detailed Statistics */}
      {scheduledInterviews.length > 0 && (
        <div className="stats-summary">
          <div className="stat-item">
            <span className="stat-number">{stats.total}</span>
            <span className="stat-label">Total Interviews</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{stats.successful}</span>
            <span className="stat-label">Fully Successful</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{stats.calendarSuccess}</span>
            <span className="stat-label">Calendar Created</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">{stats.emailSuccess}</span>
            <span className="stat-label">Emails Sent</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">
              {stats.total > 0 ? Math.round((stats.successful / stats.total) * 100) : 0}%
            </span>
            <span className="stat-label">Success Rate</span>
          </div>
        </div>
      )}

      {/* Next Steps */}
      {scheduledInterviews.length > 0 && (
        <div style={{ 
          marginTop: '2rem', 
          padding: '1.5rem', 
          background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1))', 
          borderRadius: '12px',
          border: '1px solid rgba(102, 126, 234, 0.2)'
        }}>
          <h3 style={{ margin: '0 0 1rem 0', color: '#333' }}>🎯 Next Steps</h3>
          <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
            <li style={{ marginBottom: '0.5rem' }}>
              Check your email for any delivery failures and resend if necessary
            </li>
            <li style={{ marginBottom: '0.5rem' }}>
              Review calendar events and add any additional details
            </li>
            <li style={{ marginBottom: '0.5rem' }}>
              Prepare interview materials and evaluation forms
            </li>
            <li style={{ marginBottom: '0.5rem' }}>
              Send reminder emails 1 day before each interview
            </li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default InterviewScheduler;