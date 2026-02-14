"""
Learning & Self-Improvement API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from models.agent_learning import (
    AgentType, FeedbackType, AgentFeedback, AgentMetrics,
    AgentLearningState
)
from services.learning_service import LearningService
from utils.database import get_db

router = APIRouter(prefix="/learning", tags=["Learning & Self-Improvement"])


def get_learning_service(db=Depends(get_db)) -> LearningService:
    """Get learning service instance"""
    return LearningService(db)


@router.post("/feedback")
async def submit_feedback(
    agent_type: AgentType,
    feedback_type: FeedbackType,
    context: Dict[str, Any],
    outcome: Dict[str, Any],
    user_rating: Optional[int] = None,
    user_comments: Optional[str] = None,
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Submit feedback for an agent action to enable learning
    
    Example:
    ```json
    {
        "agent_type": "interview",
        "feedback_type": "positive",
        "context": {
            "interview_id": "...",
            "questions": ["Tell me about your Python experience"],
            "job_level": "senior"
        },
        "outcome": {
            "candidate_hired": true,
            "interview_quality": "excellent"
        },
        "user_rating": 5,
        "user_comments": "Great questions, very relevant"
    }
    ```
    """
    feedback_id = await learning_service.record_feedback(
        agent_type=agent_type,
        feedback_type=feedback_type,
        context=context,
        outcome=outcome,
        user_rating=user_rating,
        user_comments=user_comments
    )
    
    return {
        "message": "Feedback recorded successfully",
        "feedback_id": feedback_id,
        "learning_enabled": True
    }


@router.get("/metrics")
async def get_all_agent_metrics(

    learning_service: LearningService = Depends(get_learning_service)
) -> List[AgentMetrics]:
    """Get performance metrics for all agents"""
    return await learning_service.get_all_metrics()


@router.get("/metrics/{agent_type}")
async def get_agent_metrics(
    agent_type: AgentType,
    learning_service: LearningService = Depends(get_learning_service)
) -> AgentMetrics:
    """Get performance metrics for a specific agent"""
    return await learning_service.get_agent_metrics(agent_type)


@router.get("/insights/{agent_type}")
async def get_learning_insights(
    agent_type: AgentType,
    learning_service: LearningService = Depends(get_learning_service)
) -> Dict[str, Any]:
    """
    Get detailed insights about what an agent has learned
    
    Returns:
    - Performance metrics
    - Learning state (enabled/disabled, exploration rate)
    - Top learned patterns
    - Recent feedback summary
    - Performance trend
    """
    return await learning_service.get_learning_insights(agent_type)


@router.get("/state/{agent_type}")
async def get_learning_state(
    agent_type: AgentType,
    learning_service: LearningService = Depends(get_learning_service)
) -> AgentLearningState:
    """Get current learning state configuration for an agent"""
    return await learning_service.get_learning_state(agent_type)


@router.put("/state/{agent_type}")
async def update_learning_state(
    agent_type: AgentType,
    learning_enabled: Optional[bool] = None,
    auto_adapt: Optional[bool] = None,
    exploration_rate: Optional[float] = None,
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Update learning configuration for an agent
    
    Parameters:
    - learning_enabled: Enable/disable learning
    - auto_adapt: Automatically apply learnings
    - exploration_rate: % of time to try new approaches (0.0-1.0)
    """
    updates = {}
    if learning_enabled is not None:
        updates["learning_enabled"] = learning_enabled
    if auto_adapt is not None:
        updates["auto_adapt"] = auto_adapt
    if exploration_rate is not None:
        if not 0.0 <= exploration_rate <= 1.0:
            raise HTTPException(400, "Exploration rate must be between 0.0 and 1.0")
        updates["exploration_rate"] = exploration_rate
    
    await learning_service.update_learning_state(agent_type, **updates)
    
    return {
        "message": f"Learning state updated for {agent_type}",
        "updates": updates
    }


@router.post("/interview/rate-question")
async def rate_interview_question(
    interview_id: str,
    question: str,
    rating: int,
    comments: Optional[str] = None,
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Rate an interview question to help the Interview Agent learn
    
    The agent will learn which questions are most effective
    """
    feedback_type = FeedbackType.POSITIVE if rating >= 4 else FeedbackType.NEGATIVE
    
    await learning_service.record_feedback(
        agent_type=AgentType.INTERVIEW,
        feedback_type=feedback_type,
        context={
            "interview_id": interview_id,
            "questions": [question]
        },
        outcome={"question_rated": True},
        user_rating=rating,
        user_comments=comments
    )
    
    return {"message": "Question rating recorded, agent will learn from this"}


@router.post("/cv/rate-candidate-selection")
async def rate_candidate_selection(
    candidate_id: str,
    was_hired: bool,
    rating: int,
    candidate_data: Dict[str, Any],
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Provide feedback on whether a shortlisted candidate was hired
    
    The CV Agent learns which candidate attributes correlate with successful hires
    """
    feedback_type = FeedbackType.POSITIVE if was_hired else FeedbackType.NEGATIVE
    
    await learning_service.record_feedback(
        agent_type=AgentType.CV_SHORTLISTING,
        feedback_type=feedback_type,
        context={
            "candidate_id": candidate_id,
            "candidate": candidate_data
        },
        outcome={
            "hired": was_hired,
            "final_decision": "hired" if was_hired else "rejected"
        },
        user_rating=rating
    )
    
    return {
        "message": "Candidate outcome recorded, CV Agent will improve its shortlisting",
        "learning_applied": was_hired
    }


@router.post("/email/correct-parsing")
async def correct_email_parsing(
    original_text: str,
    incorrect_result: Dict[str, Any],
    correct_result: Dict[str, Any],
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Correct an email parsing mistake
    
    The Email Agent learns from corrections to improve future parsing
    """
    await learning_service.record_feedback(
        agent_type=AgentType.EMAIL_SCHEDULING,
        feedback_type=FeedbackType.CORRECTION,
        context={
            "email_text": original_text,
            "incorrect_parsing": incorrect_result
        },
        outcome={
            "correction": correct_result,
            "corrected_by_user": True
        },
        user_rating=1  # Low rating for incorrect parsing
    )
    
    return {
        "message": "Correction recorded, Email Agent will learn from this",
        "correction_applied": True
    }


@router.get("/evolution/{agent_type}")
async def get_agent_evolution_history(
    agent_type: AgentType,
    learning_service: LearningService = Depends(get_learning_service)
):
    """
    Get the evolution history of an agent's prompts and behavior
    
    Shows how the agent has improved over time
    """
    evolution_history = await learning_service.prompt_evolution_collection.find({
        "agent_type": agent_type
    }).sort("created_at", 1).to_list(length=100)
    
    return {
        "agent_type": agent_type,
        "total_versions": len(evolution_history),
        "evolution_history": evolution_history,
        "performance_trend": [
            {
                "version": item["prompt_version"],
                "performance_score": item["performance_score"],
                "created_at": item["created_at"]
            }
            for item in evolution_history
        ]
    }
