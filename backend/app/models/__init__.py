"""
Models Package

This package contains all the data models and schemas used in the HR AI Agent application.
It includes Pydantic models for API request/response validation and database schemas.

Modules:
    schemas: Contains Pydantic models for API validation and serialization
"""

from app.models.schemas import (
    JobDescription,
    CandidateScore,
    InterviewSlot,
    EmailConfirmation
)

__all__ = [
    'JobDescription',
    'CandidateScore', 
    'InterviewSlot',
    'EmailConfirmation'
]