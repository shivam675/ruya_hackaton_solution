"""
LLM Service using Ollama
"""
from ollama import chat
from typing import List, Dict, Generator
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Ollama LLM Service for interview questions and responses"""
    
    def __init__(self, model_name: str = "ministral-3:3b"):
        self.model = model_name
        self.conversation_history: List[Dict[str, str]] = []
        logger.info(f"LLM Service initialized with model: {model_name}")
    
    def create_interviewer_prompt(self, job_description: str) -> str:
        """
        Create system prompt for interviewer
        
        Args:
            job_description: Job description text
            
        Returns:
            System prompt
        """
        return f"""You are a professional technical interviewer conducting a job interview. 

Job Description:
{job_description}

Your role:
1. Ask relevant technical and behavioral questions based on the job requirements
2. Listen carefully to candidate responses
3. Ask follow-up questions to dive deeper
4. Be professional, friendly, and encouraging
5. Keep responses concise (2-3 sentences max)
6. One question at a time
7. Format responses as ONE CONTINUOUS PARAGRAPH with NO line breaks
8. End each sentence with exactly one period followed by one space

Start the interview by introducing yourself and asking the first question based on the job description."""
    
    def initialize_interview(self, job_description: str):
        """Initialize interview with job description"""
        system_prompt = self.create_interviewer_prompt(job_description)
        self.conversation_history = [
            {'role': 'system', 'content': system_prompt}
        ]
        logger.info("✅ Interview initialized")
    
    def stream_response(self, user_input: str) -> Generator[str, None, None]:
        """
        Stream LLM response for user input
        
        Args:
            user_input: Candidate's response
            
        Yields:
            Response chunks
        """
        # Add user message to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_input
        })
        
        logger.info(f"🤖 Generating response for: {user_input[:50]}...")
        
        # Stream response from Ollama
        stream = chat(
            model=self.model,
            messages=self.conversation_history,
            stream=True,
        )
        
        full_response = ""
        for chunk in stream:
            chunk_text = chunk.message.content
            full_response += chunk_text
            yield chunk_text
        
        # Add assistant response to history
        self.conversation_history.append({
            'role': 'assistant',
            'content': full_response
        })
        
        logger.info("✅ Response generated")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get full conversation history"""
        return self.conversation_history


# Global LLM service
llm_service = LLMService()
