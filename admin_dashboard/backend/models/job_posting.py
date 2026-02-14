"""
Job Posting Model and Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId


class JobPostingBase(BaseModel):
    """Base job posting schema"""
    title: str
    job_description: str
    required_skills: List[str] = []
    min_experience: int = 0
    max_experience: Optional[int] = None
    location: Optional[str] = None
    department: Optional[str] = None


class JobPostingCreate(JobPostingBase):
    """Job posting creation schema"""
    pass


class JobPostingUpdate(BaseModel):
    """Job posting update schema"""
    title: Optional[str] = None
    job_description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    location: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class JobPosting(JobPostingBase):
    """Job posting response schema"""
    id: str = Field(alias="_id")
    is_active: bool = True
    created_at: datetime
    created_by: Optional[str] = "system"  # User ID
    candidates_count: int = 0
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        # Ensure _id is used in serialization
        by_alias = False  # Keep _id in output


class JobPostingInDB(JobPosting):
    """Job posting in database"""
    pass
