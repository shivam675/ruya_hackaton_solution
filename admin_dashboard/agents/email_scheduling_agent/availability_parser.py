"""
Availability Parser using LLM
Extracts time slots from freeform text responses
"""
from ollama import chat
from typing import List, Dict, Any
from datetime import datetime
import logging
import json
import re

logger = logging.getLogger(__name__)


class AvailabilityParser:
    """Parse candidate availability using LLM"""
    
    def __init__(self, model_name: str = "llama3.2:1b"):
        self.model = model_name
        self.system_prompt = """You are an AI assistant that extracts time availability from email responses.

Extract all mentioned time slots and return them in this EXACT JSON format:
{
  "time_slots": [
    {
      "day": "Monday",
      "date": "2026-02-17",
      "start_time": "14:00",
      "end_time": "16:00"
    }
  ],
  "timezone": "UTC",
  "notes": "Any additional context"
}

Rules:
1. Parse dates relative to today if not specified
2. Use 24-hour format for times
3. Extract ALL mentioned time slots
4. If no clear date, estimate based on context
5. ONLY return valid JSON, nothing else

Today's date for reference: """ + datetime.now().strftime("%Y-%m-%d (%A)")
    
    def parse_availability(self, email_text: str) -> Dict[str, Any]:
        """
        Parse availability from email text using LLM
        
        Args:
            email_text: Email body text
            
        Returns:
            Parsed availability data
        """
        try:
            logger.info("🤖 Parsing availability using LLM")
            
            response = chat(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.system_prompt},
                    {'role': 'user', 'content': f"Extract availability from this email:\n\n{email_text}"}
                ],
            )
            
            response_text = response.message.content.strip()
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                logger.info(f"✅ Parsed {len(result.get('time_slots', []))} time slots")
                return result
            else:
                logger.warning("⚠️ No JSON found in LLM response")
                return {
                    "time_slots": [],
                    "timezone": "UTC",
                    "notes": "Failed to parse availability",
                    "raw_response": response_text
                }
                
        except Exception as e:
            logger.error(f"❌ Error parsing availability: {e}")
            return {
                "time_slots": [],
                "timezone": "UTC",
                "notes": f"Error: {str(e)}",
                "error": str(e)
            }
    
    def select_best_slot(self, parsed_availability: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select the best available time slot
        
        Args:
            parsed_availability: Parsed availability data
            
        Returns:
            Best time slot or None
        """
        time_slots = parsed_availability.get("time_slots", [])
        
        if not time_slots:
            return None
        
        # For now, just return the first slot
        # In production, check against interviewer availability
        return time_slots[0]


# Global parser instance
availability_parser = AvailabilityParser()
