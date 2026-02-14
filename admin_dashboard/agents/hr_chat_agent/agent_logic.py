"""
HR Chat Agent - Intelligent HR Assistant with RAG and Employee Database
Handles HR policy questions and employee information queries
"""
from typing import Dict, Any
from pathlib import Path
import json
import sys
import logging

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import with absolute imports
from tools.employee_db_tool import EmployeeDBTool
from tools.rag_policy_tool import RAGPolicyTool
from agents.reflection import ReflectionAgent
from agents.orchestrator import HROrchestrator

logger = logging.getLogger(__name__)


class HRChatAgent:
    """
    HR Chat Agent for handling employee queries
    """
    
    def __init__(self):
        # Initialize tools
        self.employee_tool = EmployeeDBTool(
            db_path=str(Path(__file__).parent / "employee_db.json")
        )
        self.rag_tool = RAGPolicyTool(
            db_dir=str(Path(__file__).parent / "chroma_db")
        )
        
        self.tools = {
            "employee_db": self.employee_tool,
            "policy_rag": self.rag_tool
        }
        
        # Initialize reflection agent
        self.reflector = ReflectionAgent(
            feedback_file=str(Path(__file__).parent / "memory" / "feedback_store.json")
        )
        
        # Initialize orchestrator
        self.orchestrator = HROrchestrator(self.tools, self.reflector)
        
        logger.info("✅ HR Chat Agent initialized")
    
    def chat(self, message: str, user_id: str = "E001") -> Dict[str, Any]:
        """
        Process a chat message and return a response
        
        Args:
            message: User's message/query
            user_id: Employee ID (default: E001)
        
        Returns:
            Dictionary with response and metadata
        """
        try:
            logger.info(f"💬 Chat request from {user_id}: {message}")
            
            # Get response from orchestrator
            response_text = self.orchestrator.handle_query(message, user_id)
            
            # Detect which tool was used
            tool_name = self.orchestrator.detect_tool(message)
            
            return {
                "response": response_text,
                "user_id": user_id,
                "tool_used": tool_name,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error in chat: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "user_id": user_id,
                "tool_used": None,
                "success": False,
                "error": str(e)
            }
    
    def submit_feedback(self, message: str, response: str, rating: int, correction: str = None, user_id: str = "E001"):
        """
        Submit feedback for a chat interaction
        
        Args:
            message: Original user message
            response: Agent's response
            rating: Rating from 1-5
            correction: Optional correction text
            user_id: Employee ID
        """
        try:
            self.reflector.store_feedback(message, response, rating, correction)
            logger.info(f"✅ Feedback stored: {rating}/5")
        except Exception as e:
            logger.error(f"❌ Error storing feedback: {e}")


# Global agent instance
hr_chat_agent = HRChatAgent()
