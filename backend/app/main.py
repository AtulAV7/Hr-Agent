from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime, timedelta

from app.models.schemas import JobDescription, CandidateScore
from app.services.resume_parser import ResumeParser
from app.services.ai_agent import AIAgent
from app.services.calendar_service import GoogleCalendarService
from app.services.email_service import EmailService
from app.utils.database import get_db, Candidate, Job
from app.config import settings

app = FastAPI(title="HR AI Agent", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Initialize services
resume_parser = ResumeParser()
ai_agent = AIAgent()
calendar_service = GoogleCalendarService()
email_service = EmailService()

# Create uploads directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Global storage for current job and candidates
current_job = None
current_candidates = []

@app.post("/api/job-description")
async def create_job_description(job_desc: JobDescription, db: Session = Depends(get_db)):
    """Create a new job description"""
    global current_job
    
    job = Job(
        title=job_desc.title,
        description=job_desc.description,
        requirements=job_desc.requirements,
        location=job_desc.location,
        department=job_desc.department,
        created_at=datetime.now()
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    current_job = job_desc
    return {"message": "Job description created", "job_id": job.id}

@app.post("/api/upload-resumes")
async def upload_resumes(files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    """Upload and process multiple resumes"""
    global current_candidates
    
    if not current_job:
        raise HTTPException(status_code=400, detail="Please create a job description first")
    
    candidates = []
    
    for file in files:
        if not file.filename.endswith('.pdf'):
            continue
            
        # Save file
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse resume
        resume_data = resume_parser.parse_resume(file_path)
        
        # AI analysis
        job_text = f"{current_job.title}\n{current_job.description}\n{current_job.requirements}"
        candidate_score = ai_agent.analyze_resume_match(
            resume_data['full_text'], 
            job_text, 
            resume_data
        )
        
        # Save to database
        candidate = Candidate(
            name=candidate_score.name,
            email=candidate_score.email,
            phone=candidate_score.phone,
            score=candidate_score.score,
            summary=candidate_score.summary,
            skills_match=str(candidate_score.skills_match),
            experience_years=candidate_score.experience_years,
            resume_path=file_path,
            created_at=datetime.now()
        )
        
        db.add(candidate)
        candidates.append(candidate_score)
    
    db.commit()
    
    # Rank candidates
    current_candidates = ai_agent.rank_candidates(candidates)
    
    return {
        "message": f"Processed {len(candidates)} resumes",
        "candidates": current_candidates
    }

@app.get("/api/candidates")
async def get_candidates():
    """Get ranked candidates"""
    return {"candidates": current_candidates}

@app.post("/api/schedule-interviews")
async def schedule_interviews(candidate_ids: List[str]):
    """Schedule interviews for selected candidates"""
    global current_candidates
    
    selected_candidates = [c for c in current_candidates if c.candidate_id in candidate_ids]
    available_slots = calendar_service.get_available_slots()
    
    scheduled_interviews = []
    
    for i, candidate in enumerate(selected_candidates[:len(available_slots)]):
        slot_time = available_slots[i]
        
        # Schedule in calendar
        calendar_result = calendar_service.schedule_interview(
            candidate.name,
            candidate.email,
            slot_time
        )
        
        if calendar_result['status'] == 'scheduled':
            # Generate and send email
            email_body = ai_agent.generate_interview_email(
                candidate,
                {
                    'date': slot_time.strftime('%Y-%m-%d'),
                    'time': slot_time.strftime('%H:%M'),
                    'location': 'Google Meet',
                    'duration': '1 hour',
                    'interviewer': 'HR Team'
                }
            )
            
            email_result = email_service.send_interview_confirmation(
                candidate.email,
                f"Interview Invitation - {current_job.title if current_job else 'Position'}",
                email_body
            )
            
            scheduled_interviews.append({
                'candidate': candidate.name,
                'email': candidate.email,
                'interview_time': slot_time.isoformat(),
                'calendar_status': calendar_result['status'],
                'email_status': email_result['status'],
                'meet_link': calendar_result.get('meet_link')
            })
    
    return {
        "message": f"Scheduled {len(scheduled_interviews)} interviews",
        "interviews": scheduled_interviews
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)