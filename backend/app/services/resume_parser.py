import PyPDF2
import fitz  # pymupdf
import re
from typing import Dict, List, Optional
import os

class ResumeParser:
    def __init__(self):
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'[\+]?[1-9]?[0-9]{7,15}')
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pymupdf"""
        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract email and phone from resume text"""
        email_match = self.email_pattern.search(text)
        phone_match = self.phone_pattern.search(text)
        
        return {
            "email": email_match.group() if email_match else None,
            "phone": phone_match.group() if phone_match else None
        }
    
    def extract_name(self, text: str) -> str:
        """Extract candidate name from resume"""
        lines = text.split('\n')
        # Usually name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 2 and len(line.split()) <= 4:
                # Simple heuristic: if it's not too long and has 1-4 words
                if not any(char.isdigit() for char in line) and '@' not in line:
                    return line
        return "Unknown Candidate"
    
    def parse_resume(self, file_path: str) -> Dict:
        """Parse complete resume and return structured data"""
        text = self.extract_text_from_pdf(file_path)
        contact_info = self.extract_contact_info(text)
        name = self.extract_name(text)
        
        return {
            "name": name,
            "email": contact_info["email"],
            "phone": contact_info["phone"],
            "full_text": text,
            "file_path": file_path
        }