"""
Interview Model and Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId


class InterviewStatus(str, Enum):
    """Interview status enumeration"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QuestionAnswer(BaseModel):
    """Question and answer pair"""
    question: str
    answer: str
    timestamp: datetime


class InterviewBase(BaseModel):
    """Base interview schema"""
    candidate_id: str
    job_posting_id: str


class InterviewCreate(InterviewBase):
    """Interview creation schema"""
    scheduled_at: Optional[datetime] = None


class InterviewUpdate(BaseModel):
    """Interview update schema"""
    status: Optional[InterviewStatus] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    transcript: Optional[List[QuestionAnswer]] = None
    recording_path: Optional[str] = None
    transcript_path: Optional[str] = None
    score: Optional[float] = None
    evaluation: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class Interview(InterviewBase):
    """Interview response schema"""
    id: str = Field(alias="_id")
    status: InterviewStatus = InterviewStatus.SCHEDULED
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    transcript: List[QuestionAnswer] = []
    recording_path: Optional[str] = None
    transcript_path: Optional[str] = None
    score: Optional[float] = None
    evaluation: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        # Ensure _id is used in serialization
        by_alias = False  # Keep _id in output


class InterviewInDB(Interview):
    """Interview in database"""
    pass


class CandidateInterviewAuth(BaseModel):
    """Candidate authentication for interview"""
    name: str


class InterviewWebSocketMessage(BaseModel):
    """WebSocket message structure"""
    type: str  # "audio", "text", "control", "transcript"
    data: Any
    timestamp: Optional[datetime] = None
