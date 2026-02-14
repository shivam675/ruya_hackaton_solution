"""
MongoDB Model for Prompt Improvements and Evaluations
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Supported agent types"""
    CV_SHORTLISTING = "cv_shortlisting"
    HR_CHAT = "hr_chat"
    EMAIL_SCHEDULING = "email_scheduling"
    INTERVIEW = "interview"


class EvaluationStatus(str, Enum):
    """Status of prompt improvement evaluation"""
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class PerformanceMetrics(BaseModel):
    """Performance metrics for an agent"""
    avg_feedback_rating: Optional[float] = Field(None, description="Average user rating (1-5)")
    success_rate: Optional[float] = Field(None, description="Task success rate (0-1)")
    total_interactions: Optional[int] = Field(0, description="Total number of interactions")
    input_output_pairs: Optional[List[Dict[str, Any]]] = Field(default_factory=list)


class PromptImprovement(BaseModel):
    """Prompt improvement evaluation record"""
    evaluation_id: str = Field(..., description="Unique evaluation ID")
    agent_type: AgentType = Field(..., description="Type of agent evaluated")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    current_prompt: str = Field(..., description="Current system prompt")
    improved_prompt: str = Field(..., description="Improved system prompt")
    evaluation_score: Optional[float] = Field(None, description="Evaluation score (1-10)")
    issues_identified: List[str] = Field(default_factory=list, description="Issues found")
    improvement_reasoning: str = Field(..., description="Why improvements are needed")
    expected_improvements: List[str] = Field(default_factory=list, description="Expected benefits")
    performance_metrics: PerformanceMetrics = Field(..., description="Performance data")
    status: EvaluationStatus = Field(EvaluationStatus.PENDING_REVIEW, description="Approval status")
    approved_at: Optional[datetime] = Field(None, description="When approved")
    rejected_at: Optional[datetime] = Field(None, description="When rejected")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection")
    approved_by: Optional[str] = Field(None, description="User who approved")
    rejected_by: Optional[str] = Field(None, description="User who rejected")
    
    class Config:
        json_schema_extra = {
            "example": {
                "evaluation_id": "cv_shortlisting_20260214_153045",
                "agent_type": "cv_shortlisting",
                "current_prompt": "You are a CV screening specialist...",
                "improved_prompt": "You are an expert CV screening specialist with 10+ years...",
                "evaluation_score": 7.5,
                "issues_identified": ["Too generic", "Lacks specificity on scoring"],
                "improvement_reasoning": "Current prompt doesn't emphasize objective scoring criteria",
                "expected_improvements": ["More consistent scoring", "Better candidate ranking"],
                "status": "pending_review"
            }
        }


class AgentPromptVersion(BaseModel):
    """Version history of agent prompts"""
    agent_type: AgentType
    version: int
    prompt_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created this version")
    is_active: bool = Field(True, description="Whether this is the active prompt")
    evaluation_id: Optional[str] = Field(None, description="Related evaluation ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "hr_chat",
                "version": 3,
                "prompt_text": "You are a helpful HR assistant...",
                "is_active": True,
                "evaluation_id": "hr_chat_20260214_120000"
            }
        }


class EvaluationRequest(BaseModel):
    """Request to evaluate an agent"""
    agent_type: AgentType = Field(..., description="Agent to evaluate")
    limit_samples: Optional[int] = Field(10, description="Number of samples to analyze")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agent_type": "cv_shortlisting",
                "limit_samples": 15
            }
        }


class ApprovalRequest(BaseModel):
    """Request to approve/reject an improvement"""
    evaluation_id: str = Field(..., description="Evaluation ID to approve/reject")
    reason: Optional[str] = Field(None, description="Optional reason (for rejection)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "evaluation_id": "cv_shortlisting_20260214_153045",
                "reason": "Improvements not aligned with business requirements"
            }
        }
