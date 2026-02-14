"""
Critic Agent API Routes - Agent Performance Evaluation and Prompt Improvement
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from models.prompt_improvement import (
    AgentType, EvaluationStatus, PromptImprovement,
    EvaluationRequest, ApprovalRequest, PerformanceMetrics
)
import sys
from pathlib import Path
import logging
import importlib.util

# Add critic_agent to path first for imports
critic_agent_dir = Path(__file__).parent.parent.parent / "agents" / "critic_agent"
sys.path.insert(0, str(critic_agent_dir))

# Import critic agent using importlib to avoid conflicts
critic_agent_path = critic_agent_dir / "agent_logic.py"
spec = importlib.util.spec_from_file_location("critic_agent_logic", critic_agent_path)
critic_module = importlib.util.module_from_spec(spec)
sys.modules['critic_agent_logic'] = critic_module  # Register in sys.modules
spec.loader.exec_module(critic_module)
critic_agent = critic_module.critic_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/critic", tags=["Critic Agent"])


@router.post("/evaluate")
async def evaluate_agent(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger evaluation of an agent's performance and get prompt improvements
    
    This will:
    1. Gather recent performance data (feedback, success rates)
    2. Call the critic agent to analyze performance
    3. Generate improved system prompt suggestions
    4. Store results for admin review
    
    Example:
    ```json
    {
        "agent_type": "cv_shortlisting",
        "limit_samples": 15
    }
    ```
    """
    try:
        # Get current prompt
        current_prompt = critic_agent.get_current_prompt(request.agent_type.value)
        
        # Get performance data (this would come from database in production)
        # For now, we'll use sample data
        performance_data = await _get_agent_performance_data(
            request.agent_type.value,
            limit=request.limit_samples
        )
        
        # Evaluate agent
        evaluation_result = await critic_agent.evaluate_agent(
            agent_type=request.agent_type.value,
            current_prompt=current_prompt,
            performance_data=performance_data
        )
        
        return {
            "message": "Agent evaluation completed",
            "evaluation_id": evaluation_result["evaluation_id"],
            "evaluation": evaluation_result
        }
        
    except Exception as e:
        logger.error(f"Error evaluating agent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@router.get("/improvements")
async def list_improvements(
    agent_type: Optional[AgentType] = None,
    status: Optional[EvaluationStatus] = None
) -> List[Dict[str, Any]]:
    """
    Get list of all prompt improvement evaluations
    
    Query parameters:
    - agent_type: Filter by agent type
    - status: Filter by status (pending_review, approved, rejected)
    """
    try:
        agent_type_str = agent_type.value if agent_type else None
        status_str = status.value if status else None
        
        evaluations = critic_agent.list_evaluations(
            agent_type=agent_type_str,
            status=status_str
        )
        
        return evaluations
        
    except Exception as e:
        logger.error(f"Error listing improvements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list improvements: {str(e)}")


@router.get("/improvements/{evaluation_id}")
async def get_improvement(
    evaluation_id: str
) -> Dict[str, Any]:
    """
    Get details of a specific improvement evaluation
    """
    try:
        evaluation = critic_agent.get_evaluation(evaluation_id)
        return evaluation
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting improvement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get improvement: {str(e)}")


@router.post("/improvements/{evaluation_id}/approve")
async def approve_improvement(
    evaluation_id: str
):
    """
    Approve and apply a prompt improvement
    
    This will:
    1. Mark the evaluation as approved
    2. Apply the improved prompt to the agent
    3. Create a version history record
    """
    try:
        updated_evaluation = critic_agent.approve_improvement(evaluation_id)
        
        return {
            "message": "Improvement approved and applied",
            "evaluation_id": evaluation_id,
            "agent_type": updated_evaluation["agent_type"],
            "applied_at": updated_evaluation["approved_at"]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error approving improvement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to approve improvement: {str(e)}")


@router.post("/improvements/{evaluation_id}/reject")
async def reject_improvement(
    evaluation_id: str,
    request: ApprovalRequest
):
    """
    Reject a prompt improvement
    
    Example:
    ```json
    {
        "evaluation_id": "cv_shortlisting_20260214_153045",
        "reason": "Improvements not aligned with business requirements"
    }
    ```
    """
    try:
        updated_evaluation = critic_agent.reject_improvement(
            evaluation_id,
            reason=request.reason
        )
        
        return {
            "message": "Improvement rejected",
            "evaluation_id": evaluation_id,
            "agent_type": updated_evaluation["agent_type"],
            "rejected_at": updated_evaluation["rejected_at"],
            "reason": request.reason
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error rejecting improvement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reject improvement: {str(e)}")


@router.get("/prompt/{agent_type}")
async def get_current_prompt(
    agent_type: AgentType
) -> Dict[str, str]:
    """
    Get the current active system prompt for an agent
    """
    try:
        prompt = critic_agent.get_current_prompt(agent_type.value)
        
        return {
            "agent_type": agent_type.value,
            "current_prompt": prompt
        }
        
    except Exception as e:
        logger.error(f"Error getting prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get prompt: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if critic agent service is healthy"""
    try:
        # Test Ollama connection
        test_context = "Test evaluation"
        # Just check if agent is initialized
        return {
            "status": "healthy",
            "model": critic_agent.model_name,
            "ollama_url": critic_agent.ollama_url
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Helper function to get agent performance data
async def _get_agent_performance_data(agent_type: str, limit: int = 10) -> Dict[str, Any]:
    """
    Get performance data for an agent
    
    In production, this would query the database for:
    - Recent feedback ratings
    - Success/failure rates
    - Input-output pairs
    
    For now, returns sample data
    """
    
    # Sample data for different agent types
    sample_data = {
        "cv_shortlisting": {
            "avg_feedback_rating": 3.8,
            "success_rate": 0.75,
            "total_interactions": 45,
            "input_output_pairs": [
                {
                    "input": "Filter candidates for Senior Python Developer role",
                    "output": "Shortlisted 8 candidates out of 30 based on Python skills and 5+ years experience",
                    "rating": 4,
                    "success": True
                },
                {
                    "input": "Find candidates for Junior Frontend position",
                    "output": "Shortlisted 12 candidates with React/Vue experience",
                    "rating": 3,
                    "success": True
                },
                {
                    "input": "Screen candidates for DevOps Engineer",
                    "output": "Found 5 candidates with AWS and Docker skills",
                    "rating": 5,
                    "success": True
                }
            ]
        },
        "hr_chat": {
            "avg_feedback_rating": 4.2,
            "success_rate": 0.85,
            "total_interactions": 120,
            "input_output_pairs": [
                {
                    "input": "What's my leave balance?",
                    "output": "You have 14 days of annual leave remaining.",
                    "rating": 5,
                    "success": True
                },
                {
                    "input": "What's the remote work policy?",
                    "output": "Our remote work policy allows 3 days per week...",
                    "rating": 4,
                    "success": True
                },
                {
                    "input": "How do I apply for parental leave?",
                    "output": "To apply for parental leave, submit a request through the HR portal...",
                    "rating": 4,
                    "success": True
                }
            ]
        },
        "email_scheduling": {
            "avg_feedback_rating": 3.5,
            "success_rate": 0.70,
            "total_interactions": 30,
            "input_output_pairs": [
                {
                    "input": "Parse candidate availability from email",
                    "output": "Extracted: Mon-Tue 2-5pm, Wed 10am-12pm",
                    "rating": 3,
                    "success": True
                },
                {
                    "input": "Schedule interview with John Doe",
                    "output": "Scheduled for Tuesday at 3pm",
                    "rating": 4,
                    "success": True
                },
                {
                    "input": "Find common availability slots",
                    "output": "Common slots: Tue 2pm, Wed 11am, Thu 4pm",
                    "rating": 3,
                    "success": True
                }
            ]
        },
        "interview": {
            "avg_feedback_rating": 4.0,
            "success_rate": 0.80,
            "total_interactions": 25,
            "input_output_pairs": [
                {
                    "input": "Conduct interview for Python Developer",
                    "output": "Asked 10 technical questions, evaluated responses, candidate scored 7/10",
                    "rating": 4,
                    "success": True
                },
                {
                    "input": "Interview for project manager role",
                    "output": "Evaluated leadership and communication skills, candidate performed well",
                    "rating": 4,
                    "success": True
                },
                {
                    "input": "Technical assessment for senior engineer",
                    "output": "System design and coding questions completed, strong performance",
                    "rating": 5,
                    "success": True
                }
            ]
        }
    }
    
    data = sample_data.get(agent_type, {
        "avg_feedback_rating": 3.0,
        "success_rate": 0.5,
        "total_interactions": 10,
        "input_output_pairs": []
    })
    
    # Limit input-output pairs
    if data.get("input_output_pairs"):
        data["input_output_pairs"] = data["input_output_pairs"][:limit]
    
    return data
