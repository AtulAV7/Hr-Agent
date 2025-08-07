"""
Services Package

This package contains all the service classes and business logic for the HR AI Agent application.
Each service handles a specific domain of functionality.

Modules:
    resume_parser: Handles PDF resume parsing and text extraction
    ai_agent: Manages AI-powered candidate analysis and ranking
    calendar_service: Integrates with Google Calendar for interview scheduling
    email_service: Handles email notifications and confirmations
"""

from app.services.resume_parser import ResumeParser
from app.services.ai_agent import AIAgent
from app.services.calendar_service import GoogleCalendarService
from app.services.email_service import EmailService

__all__ = [
    'ResumeParser',
    'AIAgent',
    'GoogleCalendarService',
    'EmailService'
]