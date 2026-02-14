"""
HR Chat Routes - API endpoints for HR chatbot
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import logging
import sys
from pathlib import Path
import importlib.util

# Add hr_chat_agent and its subdirectories to path for imports
hr_chat_agent_dir = Path(__file__).parent.parent.parent / "agents" / "hr_chat_agent"
sys.path.insert(0, str(hr_chat_agent_dir))
sys.path.insert(0, str(hr_chat_agent_dir / "tools"))
sys.path.insert(0, str(hr_chat_agent_dir / "agents"))

# Import HR chat agent using importlib
hr_chat_agent_path = hr_chat_agent_dir / "agent_logic.py"
spec = importlib.util.spec_from_file_location("hr_agent_logic", hr_chat_agent_path)
hr_agent_module = importlib.util.module_from_spec(spec)
sys.modules['hr_agent_logic'] = hr_agent_module  # Register in sys.modules
spec.loader.exec_module(hr_agent_module)
hr_chat_agent = hr_agent_module.hr_chat_agent

router = APIRouter(prefix="/hr-chat", tags=["HR Chat"])
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    message: str
    user_id: str = "E001"


class FeedbackSubmission(BaseModel):
    message: str
    response: str
    rating: int
    correction: str = None
    user_id: str = "E001"


@router.post("/message")
async def send_message(
    chat_message: ChatMessage
):
    """
    Send a message to the HR chat agent and get a response
    """
    try:
        logger.info(f"💬 HR Chat message: {chat_message.message}")
        
        # Get response from HR agent
        result = hr_chat_agent.chat(
            message=chat_message.message,
            user_id=chat_message.user_id
        )
        
        logger.info(f"✅ HR Agent responded using {result.get('tool_used')}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in HR chat: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat message: {str(e)}"
        )


@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackSubmission
):
    """
    Submit feedback for a chat interaction
    """
    try:
        hr_chat_agent.submit_feedback(
            message=feedback.message,
            response=feedback.response,
            rating=feedback.rating,
            correction=feedback.correction,
            user_id=feedback.user_id
        )
        
        logger.info(f"✅ Feedback stored: {feedback.rating}/5")
        
        return {"message": "Feedback submitted successfully"}
        
    except Exception as e:
        logger.error(f"❌ Error storing feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting feedback: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check for HR chat agent"""
    return {
        "status": "healthy",
        "agent": "HR Chat Agent",
        "ready": True
    }
