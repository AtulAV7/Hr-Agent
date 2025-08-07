"""
HR AI Agent Application

This module contains the main application for the HR AI Agent system.
It provides automated resume screening, candidate ranking, interview scheduling,
and email confirmation capabilities.

Author: HR AI Agent Team
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "HR AI Agent Team"
__email__ = "support@hraiagent.com"

# Application metadata
APP_NAME = "HR AI Agent"
APP_DESCRIPTION = "Automated Resume Screening and Interview Scheduling System"

# Import main components for easy access
from app.main import app
from app.config import settings
from app.models import schemas
from app.services import resume_parser, ai_agent, calendar_service, email_service
from app.utils import database

__all__ = [
    'app',
    'settings',
    'schemas',
    'resume_parser',
    'ai_agent',
    'calendar_service',
    'email_service',
    'database'
]