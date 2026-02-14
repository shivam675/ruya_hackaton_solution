from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    """Types of agents in the system"""
    CV_SHORTLISTING = "cv_shortlisting"
    INTERVIEW = "interview"
    EMAIL_SCHEDULING = "email_scheduling"
    HR_CHAT = "hr_chat"


class FeedbackType(str, Enum):
    """Types of feedback for learning"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    CORRECTION = "correction"


class LearningPattern(BaseModel):
    """A learned pattern that improves agent performance"""
    pattern_id: str
    agent_type: AgentType
    pattern_type: str  # e.g., "prompt_template", "scoring_weight", "question_type"
    pattern_data: Dict[str, Any]
    success_rate: float = 0.0
    usage_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None
    is_active: bool = True


class AgentFeedback(BaseModel):
    """Feedback on agent performance for learning"""
    feedback_id: Optional[str] = None
    agent_type: AgentType
    feedback_type: FeedbackType
    context: Dict[str, Any]  # What the agent did
    outcome: Dict[str, Any]  # What happened
    user_rating: Optional[int] = Field(None, ge=1, le=5)
    user_comments: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = False


class AgentMetrics(BaseModel):
    """Performance metrics for an agent"""
    agent_type: AgentType
    version: str = "1.0.0"
    total_actions: int = 0
    successful_actions: int = 0
    failed_actions: int = 0
    average_rating: float = 0.0
    improvement_rate: float = 0.0  # % improvement over baseline
    patterns_learned: int = 0
    last_improvement_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InterviewQuestionPattern(BaseModel):
    """Learned patterns for interview questions"""
    question_template: str
    job_level: str  # junior, mid, senior
    skill_area: str  # technical, behavioral, cultural
    success_rate: float = 0.0
    avg_candidate_rating: float = 0.0
    avg_hr_rating: float = 0.0
    times_used: int = 0
    generated_questions: List[str] = []


class CVScoringPattern(BaseModel):
    """Learned patterns for CV scoring"""
    skill: str
    weight: float = 1.0
    hire_correlation: float = 0.0  # How correlated this skill is with hiring
    times_evaluated: int = 0
    hired_count: int = 0
    rejected_count: int = 0


class PromptEvolution(BaseModel):
    """Track evolution of prompts over time"""
    agent_type: AgentType
    prompt_version: str
    prompt_template: str
    performance_score: float = 0.0
    is_active: bool = True
    parent_version: Optional[str] = None
    improvements: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentLearningState(BaseModel):
    """Current learning state of an agent"""
    agent_type: AgentType
    learning_enabled: bool = True
    auto_adapt: bool = True  # Automatically apply learnings
    exploration_rate: float = 0.1  # % of time to try new approaches
    learned_patterns: List[str] = []  # Pattern IDs
    active_experiments: List[Dict[str, Any]] = []
    baseline_performance: float = 0.0
    current_performance: float = 0.0
    total_learnings: int = 0
    last_learning_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
