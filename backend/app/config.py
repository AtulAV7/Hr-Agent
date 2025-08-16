# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # AI Model Configuration - Gemini first, OpenAI as fallback
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Google Calendar
    GOOGLE_CALENDAR_CREDENTIALS_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE", "app/credentials.json")
    GOOGLE_CALENDAR_TOKEN_FILE = os.getenv("GOOGLE_CALENDAR_TOKEN_FILE", "token.json")
    
    # Email Configuration
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hr_agent.db")
    
    # File Upload
    UPLOAD_DIR = "uploads"

settings = Settings()