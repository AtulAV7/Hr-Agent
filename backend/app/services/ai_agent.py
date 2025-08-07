from openai import OpenAI
import json
from typing import List, Dict
from app.config import settings
from app.models.schemas import CandidateScore

class AIAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def analyze_resume_match(self, resume_text: str, job_description: str, candidate_info: Dict) -> CandidateScore:
        """Analyze resume against job description and return scoring"""
        
        prompt = f"""
        You are an expert HR AI agent. Analyze the following resume against the job description and provide a detailed assessment.

        JOB DESCRIPTION:
        {job_description}

        RESUME TEXT:
        {resume_text}

        CANDIDATE INFO:
        Name: {candidate_info.get('name', 'Unknown')}
        Email: {candidate_info.get('email', 'No email')}
        Phone: {candidate_info.get('phone', 'No phone')}

        Please provide your analysis in the following JSON format:
        {{
            "score": <float between 0-100>,
            "summary": "<brief summary of candidate strengths and fit>",
            "skills_match": ["<list of matching skills>"],
            "experience_years": <estimated years of experience>,
            "strengths": ["<key strengths>"],
            "concerns": ["<potential concerns>"],
            "recommendation": "<hire/interview/reject with brief reason>"
        }}

        Be thorough but concise in your analysis.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert HR AI agent specializing in resume analysis and candidate evaluation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            return CandidateScore(
                candidate_id=f"cand_{hash(candidate_info.get('email', 'unknown'))}",
                name=candidate_info.get('name', 'Unknown'),
                email=candidate_info.get('email', 'no-email@example.com'),
                phone=candidate_info.get('phone'),
                score=analysis['score'],
                summary=analysis['summary'],
                skills_match=analysis['skills_match'],
                experience_years=analysis.get('experience_years'),
                resume_path=candidate_info.get('file_path', '')
            )
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            # Return default score for failed analysis
            return CandidateScore(
                candidate_id=f"cand_{hash(candidate_info.get('email', 'unknown'))}",
                name=candidate_info.get('name', 'Unknown'),
                email=candidate_info.get('email', 'no-email@example.com'),
                phone=candidate_info.get('phone'),
                score=0.0,
                summary="Analysis failed - manual review required",
                skills_match=[],
                experience_years=0,
                resume_path=candidate_info.get('file_path', '')
            )
    
    def rank_candidates(self, candidates: List[CandidateScore]) -> List[CandidateScore]:
        """Rank candidates by score"""
        return sorted(candidates, key=lambda x: x.score, reverse=True)
    
    def generate_interview_email(self, candidate: CandidateScore, interview_details: Dict) -> str:
        """Generate personalized interview confirmation email"""
        
        prompt = f"""
        Generate a professional, personalized interview confirmation email for the following candidate:

        Candidate: {candidate.name}
        Email: {candidate.email}
        Score: {candidate.score}
        Summary: {candidate.summary}

        Interview Details:
        Date: {interview_details.get('date')}
        Time: {interview_details.get('time')}
        Location: {interview_details.get('location', 'Google Meet')}
        Duration: {interview_details.get('duration', '1 hour')}
        Interviewer: {interview_details.get('interviewer', 'HR Team')}

        Make it professional, welcoming, and include all necessary details.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional HR assistant generating interview confirmation emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating email: {e}")
            return f"Dear {candidate.name},\n\nWe are pleased to invite you for an interview.\n\nBest regards,\nHR Team"