import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_CALENDAR_CREDENTIALS_FILE = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE", "credentials.json")
    GOOGLE_CALENDAR_TOKEN_FILE = os.getenv("GOOGLE_CALENDAR_TOKEN_FILE", "token.json")
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hr_agent.db")
    UPLOAD_DIR = "uploads"

settings = Settings()