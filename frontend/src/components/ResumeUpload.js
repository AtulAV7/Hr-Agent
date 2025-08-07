import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const ResumeUpload = ({ onResumesUpload, disabled }) => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    const pdfFiles = acceptedFiles.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length === 0) {
      alert('Please upload only PDF files.');
      return;
    }

    if (pdfFiles.length !== acceptedFiles.length) {
      alert('Some files were rejected. Please upload only PDF files.');
    }

    setUploadedFiles(prev => [...prev, ...pdfFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    disabled: disabled || uploading
  });

  const removeFile = (fileToRemove) => {
    setUploadedFiles(files => files.filter(file => file !== fileToRemove));
  };

  const handleUpload = async () => {
    if (uploadedFiles.length === 0) {
      alert('Please select at least one PDF file to upload.');
      return;
    }

    setUploading(true);
    
    try {
      const formData = new FormData();
      uploadedFiles.forEach(file => {
        formData.append('files', file);
      });

      await onResumesUpload(formData);
      
      // Clear uploaded files after successful upload
      setUploadedFiles([]);
      
    } catch (error) {
      console.error('Upload failed:', error);
      // Error is handled by parent component
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="resume-upload">
      <h2>📄 Upload Resume Files</h2>
      <p>Upload PDF resumes to analyze and rank candidates</p>
      
      <div 
        {...getRootProps()} 
        className={`dropzone ${isDragActive ? 'active' : ''} ${disabled || uploading ? 'disabled' : ''}`}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the PDF files here...</p>
        ) : (
          <div>
            <p>Drag & drop PDF resume files here, or click to select files</p>
            <p style={{ fontSize: '0.9rem', color: '#666', marginTop: '0.5rem' }}>
              Only PDF files are accepted
            </p>
          </div>
        )}
      </div>

      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h3>📋 Selected Files ({uploadedFiles.length})</h3>
          <ul>
            {uploadedFiles.map((file, index) => (
              <li key={index}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong>{file.name}</strong>
                    <span style={{ marginLeft: '1rem', color: '#666', fontSize: '0.9rem' }}>
                      ({formatFileSize(file.size)})
                    </span>
                  </div>
                  <button 
                    type="button"
                    onClick={() => removeFile(file)}
                    style={{
                      background: '#ff4757',
                      color: 'white',
                      border: 'none',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      cursor: 'pointer'
                    }}
                    disabled={uploading}
                  >
                    Remove
                  </button>
                </div>
              </li>
            ))}
          </ul>
          
          <div style={{ marginTop: '2rem', textAlign: 'center' }}>
            <button 
              onClick={handleUpload}
              disabled={uploading || disabled}
              style={{
                padding: '1rem 2rem',
                fontSize: '1.1rem',
                fontWeight: '600'
              }}
            >
              {uploading ? '🔄 Processing Resumes...' : `🚀 Analyze ${uploadedFiles.length} Resume${uploadedFiles.length > 1 ? 's' : ''}`}
            </button>
          </div>
        </div>
      )}

      {uploadedFiles.length === 0 && (
        <div style={{ textAlign: 'center', marginTop: '2rem', color: '#666' }}>
          <p>No files selected. Please upload PDF resume files to continue.</p>
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;