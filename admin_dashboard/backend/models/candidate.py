"""
Candidate Model and Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from bson import ObjectId


class CandidateStatus(str, Enum):
    """Candidate status enumeration"""
    SHORTLISTED = "shortlisted"
    APPROVED = "approved"
    EMAIL_SENT = "email_sent"
    SCHEDULED = "scheduled"
    INTERVIEWED = "interviewed"
    SELECTED = "selected"
    REJECTED = "rejected"


class CandidateBase(BaseModel):
    """Base candidate schema"""
    name: str
    email: EmailStr
    skills: List[str] = []
    experience: int = 0
    cv_path: Optional[str] = None
    cover_letter: Optional[str] = None


class CandidateFromCV(CandidateBase):
    """Candidate data from CV agent"""
    confidence: float


class CandidateCreate(CandidateBase):
    """Candidate creation schema"""
    job_posting_id: str
    confidence: float = 0.0


class CandidateUpdate(BaseModel):
    """Candidate update schema"""
    status: Optional[CandidateStatus] = None
    interview_scheduled_at: Optional[datetime] = None
    availability_response: Optional[str] = None
    notes: Optional[str] = None


class Candidate(CandidateBase):
    """Candidate response schema"""
    id: str = Field(alias="_id")
    job_posting_id: str
    confidence: float
    status: CandidateStatus = CandidateStatus.SHORTLISTED
    created_at: datetime
    interview_scheduled_at: Optional[datetime] = None
    availability_response: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        # Ensure _id is used in serialization
        by_alias = False  # Keep _id in output


class CandidateInDB(Candidate):
    """Candidate in database"""
    pass


class CandidateApproval(BaseModel):
    """Candidate approval schema"""
    candidate_ids: List[str]
    send_email: bool = True
