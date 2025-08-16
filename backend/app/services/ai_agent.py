import google.generativeai as genai
import json
import re
from typing import List, Dict
from app.config import settings
from app.models.schemas import CandidateScore

class AIAgent:
    def __init__(self):
        print(f"🔧 Initializing AIAgent with Google Gemini...")
        
        # Check for Gemini API key first, then OpenAI as fallback
        gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
        openai_key = getattr(settings, 'OPENAI_API_KEY', None)
        
        if gemini_key:
            print(f"✅ Gemini API Key found: {gemini_key[:10]}...")
            genai.configure(api_key=gemini_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')  # Fast and free
            self.ai_provider = "gemini"
            self.use_ai = True
            print("🤖 Using Google Gemini AI")
        elif openai_key:
            print(f"✅ OpenAI API Key found: {openai_key[:10]}...")
            from openai import OpenAI
            self.client = OpenAI(api_key=openai_key)
            self.openai_model = "gpt-3.5-turbo"
            self.ai_provider = "openai"
            self.use_ai = True
            print("🤖 Using OpenAI as fallback")
        else:
            print("⚠️ No AI API keys found - using rule-based analysis")
            self.use_ai = False
            self.ai_provider = "none"
    
    def analyze_resume_match(self, resume_text: str, job_description: str, candidate_info: Dict) -> CandidateScore:
        """Analyze resume against job description using Gemini or fallback"""
        
        print(f"\n📋 Starting analysis for: {candidate_info.get('name', 'Unknown')}")
        print(f"🤖 AI Provider: {self.ai_provider}")
        
        # Try AI analysis first
        if self.use_ai:
            try:
                if self.ai_provider == "gemini":
                    return self._gemini_analysis(resume_text, job_description, candidate_info)
                elif self.ai_provider == "openai":
                    return self._openai_analysis(resume_text, job_description, candidate_info)
            except Exception as e:
                error_str = str(e)
                print(f"❌ AI analysis failed: {error_str}")
                
                # Check for quota/rate limit errors
                if any(term in error_str.lower() for term in ["quota", "limit", "billing", "429", "403"]):
                    print("💡 Switching to rule-based analysis due to API limits")
                    self.use_ai = False
        
        # Fallback to rule-based analysis
        print("🔄 Using rule-based analysis...")
        return self._rule_based_analysis(resume_text, job_description, candidate_info)
    
    def _gemini_analysis(self, resume_text: str, job_description: str, candidate_info: Dict) -> CandidateScore:
        """AI analysis using Google Gemini"""
        
        prompt = f"""
        You are an expert HR AI agent. Analyze this resume against the job description and provide a detailed assessment.

        **JOB DESCRIPTION:**
        {job_description}

        **RESUME:**
        {resume_text[:2000]}  # Limit to avoid token limits

        **CANDIDATE INFO:**
        - Name: {candidate_info.get('name', 'Unknown')}
        - Email: {candidate_info.get('email', 'No email')}
        - Phone: {candidate_info.get('phone', 'No phone')}

        **INSTRUCTIONS:**
        Provide your analysis in exactly this JSON format (no markdown, no extra text):

        {{
            "score": 75.5,
            "summary": "Brief summary of candidate strengths and fit for the role",
            "skills_match": ["skill1", "skill2", "skill3"],
            "experience_years": 3,
            "strengths": ["strength1", "strength2"],
            "concerns": ["concern1", "concern2"],
            "recommendation": "interview - good technical background"
        }}

        Score the candidate 0-100 based on:
        - Skills alignment with job requirements (40%)
        - Relevant experience and years (30%)
        - Education and qualifications (20%)
        - Overall fit and potential (10%)

        Be thorough but concise in your analysis.
        """
        
        print("🔮 Calling Gemini API...")
        
        # Generate response
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        
        print(f"📤 Gemini Response length: {len(response_text)} chars")
        print(f"📝 Response preview: {response_text[:200]}...")
        
        # Extract JSON from response
        try:
            # Try direct JSON parsing first
            analysis = json.loads(response_text)
            print("✅ Direct JSON parsing successful!")
        except json.JSONDecodeError:
            # Try to extract JSON from markdown or text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                try:
                    analysis = json.loads(json_text)
                    print("✅ JSON extraction successful!")
                except json.JSONDecodeError:
                    # Clean common JSON issues
                    json_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', json_text)
                    json_text = json_text.replace("'", '"')
                    analysis = json.loads(json_text)
                    print("✅ JSON cleaning and parsing successful!")
            else:
                raise ValueError("No valid JSON found in response")
        
        # Create candidate score object
        candidate_score = CandidateScore(
            candidate_id=f"cand_{hash(candidate_info.get('email', 'unknown'))}",
            name=candidate_info.get('name', 'Unknown'),
            email=candidate_info.get('email', 'no-email@example.com'),
            phone=candidate_info.get('phone'),
            score=float(analysis.get('score', 0)),
            summary=analysis.get('summary', 'AI analysis completed'),
            skills_match=analysis.get('skills_match', []),
            experience_years=int(analysis.get('experience_years', 0)),
            resume_path=candidate_info.get('file_path', '')
        )
        
        print(f"✅ Gemini analysis completed! Score: {candidate_score.score}")
        return candidate_score
    
    def _openai_analysis(self, resume_text: str, job_description: str, candidate_info: Dict) -> CandidateScore:
        """Fallback OpenAI analysis"""
        
        prompt = f"""
        Analyze this resume against the job description. Return ONLY valid JSON:

        {{
            "score": 75.5,
            "summary": "Brief assessment",
            "skills_match": ["skill1", "skill2"],
            "experience_years": 3,
            "strengths": ["strength1"],
            "concerns": ["concern1"],
            "recommendation": "interview"
        }}

        Job: {job_description[:500]}
        Resume: {resume_text[:1500]}
        """
        
        response = self.client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": "You are an HR analyst. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        return CandidateScore(
            candidate_id=f"cand_{hash(candidate_info.get('email', 'unknown'))}",
            name=candidate_info.get('name', 'Unknown'),
            email=candidate_info.get('email', 'no-email@example.com'),
            phone=candidate_info.get('phone'),
            score=float(analysis['score']),
            summary=analysis['summary'],
            skills_match=analysis['skills_match'],
            experience_years=analysis.get('experience_years', 0),
            resume_path=candidate_info.get('file_path', '')
        )
    
    def _rule_based_analysis(self, resume_text: str, job_description: str, candidate_info: Dict) -> CandidateScore:
        """Advanced rule-based analysis fallback"""
        
        resume_lower = resume_text.lower()
        job_lower = job_description.lower()
        
        # Extract basic info
        name = candidate_info.get('name', self._extract_name(resume_text))
        email = candidate_info.get('email', self._extract_email(resume_text))
        phone = candidate_info.get('phone', self._extract_phone(resume_text))
        
        # Skill matching
        tech_skills = {
            'programming': ['python', 'javascript', 'java', 'c++', 'react', 'node', 'angular'],
            'data': ['sql', 'mysql', 'postgresql', 'mongodb', 'pandas', 'numpy'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'web': ['html', 'css', 'bootstrap', 'rest api'],
            'mobile': ['android', 'ios', 'flutter', 'react native'],
            'devops': ['git', 'jenkins', 'ci/cd', 'linux']
        }
        
        skill_matches = []
        skill_score = 0
        
        for category, skills in tech_skills.items():
            for skill in skills:
                if skill in resume_lower and skill in job_lower:
                    skill_matches.append(skill)
                    skill_score += 15
                elif skill in resume_lower:
                    skill_score += 5
        
        # Experience scoring
        experience_years = self._extract_experience_years(resume_text)
        experience_score = min(30, experience_years * 5)
        
        # Education scoring
        education_keywords = ['bachelor', 'master', 'degree', 'university', 'computer science', 'engineering']
        education_score = 10 if any(kw in resume_lower for kw in education_keywords) else 0
        
        # Job title relevance
        job_titles = ['developer', 'engineer', 'programmer', 'analyst']
        title_score = 20 if any(title in resume_lower and title in job_lower for title in job_titles) else 0
        
        total_score = min(100, skill_score + experience_score + education_score + title_score)
        
        # Generate summary
        strengths = []
        if skill_matches:
            strengths.append(f"Technical skills: {', '.join(skill_matches[:3])}")
        if experience_years >= 2:
            strengths.append(f"{experience_years} years experience")
        if education_score > 0:
            strengths.append("Relevant education")
        
        summary = f"Rule-based analysis: {total_score}/100. " + (
            f"Key match: {strengths[0]}" if strengths else "Needs detailed review"
        )
        
        print(f"✅ Rule-based analysis completed! Score: {total_score}")
        
        return CandidateScore(
            candidate_id=f"cand_{hash(candidate_info.get('email', 'unknown'))}",
            name=name,
            email=email,
            phone=phone,
            score=float(total_score),
            summary=summary,
            skills_match=skill_matches,
            experience_years=experience_years,
            resume_path=candidate_info.get('file_path', '')
        )
    
    def _extract_name(self, text: str) -> str:
        lines = text.split('\n')[:5]
        for line in lines:
            line = line.strip()
            if 2 <= len(line.split()) <= 4 and len(line) < 50 and '@' not in line:
                if re.match(r'^[A-Za-z\s.]+$', line):
                    return line.title()
        return "Unknown Candidate"
    
    def _extract_email(self, text: str) -> str:
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(pattern, text)
        return emails[0] if emails else ""
    
    def _extract_phone(self, text: str) -> str:
        patterns = [
            r'[\+]?[1-9]?[\d\s\-\(\)]{10,15}',
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        for pattern in patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0].strip()
        return ""
    
    def _extract_experience_years(self, text: str) -> int:
        patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                try:
                    return int(matches[0])
                except:
                    continue
        
        # Estimate from date ranges
        date_ranges = re.findall(r'20\d{2}\s*[-–]\s*(?:20\d{2}|present)', text.lower())
        if date_ranges:
            return max(1, len(date_ranges) * 2)
        
        return 1
    
    def rank_candidates(self, candidates: List[CandidateScore]) -> List[CandidateScore]:
        """Rank candidates by score"""
        ranked = sorted(candidates, key=lambda x: x.score, reverse=True)
        print(f"📊 Ranked {len(candidates)} candidates")
        return ranked
    
    def generate_interview_email(self, candidate: CandidateScore, interview_details: Dict) -> str:
        """Generate interview email using AI or template"""
        
        if self.use_ai and self.ai_provider == "gemini":
            try:
                prompt = f"""
                Write a professional interview invitation email for {candidate.name}.
                
                Details:
                - Date: {interview_details.get('date')}
                - Time: {interview_details.get('time')}
                - Location: {interview_details.get('location', 'Virtual')}
                
                Keep it professional, welcoming, and concise (under 150 words).
                """
                
                response = self.model.generate_content(prompt)
                return response.text.strip()
                
            except Exception as e:
                print(f"❌ Email generation failed: {e}")
        
        # Template fallback
        return f"""Dear {candidate.name},

Thank you for your interest in our position. We are pleased to invite you for an interview.

Interview Details:
• Date: {interview_details.get('date', 'To be scheduled')}
• Time: {interview_details.get('time', 'To be confirmed')}
• Duration: {interview_details.get('duration', '1 hour')}
• Location: {interview_details.get('location', 'Virtual Meeting')}

Please confirm your attendance by replying to this email.

Best regards,
HR Team"""