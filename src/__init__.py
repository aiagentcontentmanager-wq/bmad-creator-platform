"""
BMAD System Package

This package contains all the core components of the BMAD system.
"""

__version__ = "1.0.0"
__author__ = "BMAD Team"
__description__ = "AI-powered recruitment and content management system"

from .database.database import Database
from .agents.recruiter_agent import RecruiterAgent
from .agents.communication_service import CommunicationService

__all__ = [
    "Database",
    "RecruiterAgent",
    "CommunicationService"
]