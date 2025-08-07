from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict
from datetime import datetime

class JobDescription(BaseModel):
    title: str
    description: str
    requirements: str
    location: str
    department: str

class CandidateScore(BaseModel):
    candidate_id: str
    name: str
    email: EmailStr
    phone: Optional[str]
    score: float
    summary: str
    skills_match: List[str]
    experience_years: Optional[int]
    resume_path: str

class InterviewSlot(BaseModel):
    candidate_id: str
    start_time: datetime
    end_time: datetime
    interview_type: str = "Technical Interview"
    location: str = "Google Meet"

class EmailConfirmation(BaseModel):
    candidate_id: str
    subject: str
    body: str
    recipient_email: EmailStr