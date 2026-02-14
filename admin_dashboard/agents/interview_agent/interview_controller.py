"""
Interview Controller
Orchestrates STT, LLM, and TTS for interviews
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging
import json
from pathlib import Path

from stt_service import stt_service
from llm_service import llm_service
from tts_service import tts_service

logger = logging.getLogger(__name__)


class InterviewController:
    """Main controller for interview sessions"""
    
    def __init__(self):
        self.active_interviews: Dict[str, dict] = {}
        self.recordings_path = Path("../../storage/recordings")
        self.transcripts_path = Path("../../storage/transcripts")
        
        # Ensure directories exist
        self.recordings_path.mkdir(parents=True, exist_ok=True)
        self.transcripts_path.mkdir(parents=True, exist_ok=True)
    
    def start_interview(self, interview_id: str, job_description: str) -> dict:
        """
        Start a new interview session
        
        Args:
            interview_id: Unique interview ID
            job_description: Job description for context
            
        Returns:
            Interview session data
        """
        logger.info(f"🎬 Starting interview: {interview_id}")
        
        # Initialize LLM with job description
        llm_service.initialize_interview(job_description)
        
        # Get initial greeting
        greeting_chunks = []
        for chunk in llm_service.stream_response("Hello, I'm ready for the interview."):
            greeting_chunks.append(chunk)
        
        greeting = "".join(greeting_chunks)
        
        # Store interview session
        self.active_interviews[interview_id] = {
            "interview_id": interview_id,
            "job_description": job_description,
            "started_at": datetime.utcnow().isoformat(),
            "transcript": [],
            "status": "active"
        }
        
        logger.info(f"✅ Interview {interview_id} started")
        
        return {
            "interview_id": interview_id,
            "status": "started",
            "greeting": greeting
        }
    
    def process_candidate_response(
        self, 
        interview_id: str, 
        candidate_text: str
    ) -> Dict[str, any]:
        """
        Process candidate's spoken response
        
        Args:
            interview_id: Interview ID
            candidate_text: Transcribed candidate speech
            
        Returns:
            Interviewer's response and metadata
        """
        if interview_id not in self.active_interviews:
            raise ValueError(f"Interview {interview_id} not found")
        
        interview = self.active_interviews[interview_id]
        
        # Add to transcript
        interview["transcript"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "speaker": "candidate",
            "text": candidate_text
        })
        
        logger.info(f"💬 Candidate: {candidate_text[:50]}...")
        
        # Generate response using LLM
        response_chunks = []
        sentences = []
        current_sentence = ""
        
        for chunk in llm_service.stream_response(candidate_text):
            response_chunks.append(chunk)
            current_sentence += chunk
            
            # Detect sentence boundaries
            if chunk == '.':
                sentence = current_sentence.strip()
                if sentence and sentence != '.':
                    sentences.append(sentence)
                    
                    # Synthesize and send audio for this sentence
                    audio_bytes = tts_service.synthesize_to_bytes(sentence)
                    
                current_sentence = ""
        
        # Handle remaining text
        if current_sentence.strip():
            sentence = current_sentence.strip()
            if not sentence.endswith('.'):
                sentence += '.'
            sentences.append(sentence)
            audio_bytes = tts_service.synthesize_to_bytes(sentence)
        
        full_response = " ".join(sentences)
        
        # Add to transcript
        interview["transcript"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "speaker": "interviewer",
            "text": full_response
        })
        
        logger.info(f"🤖 Interviewer: {full_response[:50]}...")
        
        return {
            "interviewer_response": full_response,
            "sentences": sentences,
            "transcript_entry": interview["transcript"][-1]
        }
    
    def end_interview(self, interview_id: str) -> dict:
        """
        End an interview and save transcript
        
        Args:
            interview_id: Interview ID
            
        Returns:
            Final interview data
        """
        if interview_id not in self.active_interviews:
            raise ValueError(f"Interview {interview_id} not found")
        
        interview = self.active_interviews[interview_id]
        interview["status"] = "completed"
        interview["completed_at"] = datetime.utcnow().isoformat()
        
        # Save transcript
        transcript_file = self.transcripts_path / f"{interview_id}_transcript.json"
        with open(transcript_file, 'w') as f:
            json.dump(interview, f, indent=2)
        
        logger.info(f"✅ Interview {interview_id} completed. Transcript saved.")
        
        # Remove from active interviews
        completed_interview = self.active_interviews.pop(interview_id)
        
        return {
            "interview_id": interview_id,
            "status": "completed",
            "transcript_path": str(transcript_file),
            "duration": "calculated_duration",  # Calculate from timestamps
            "transcript": completed_interview["transcript"]
        }
    
    def get_interview_status(self, interview_id: str) -> dict:
        """Get current interview status"""
        if interview_id in self.active_interviews:
            return self.active_interviews[interview_id]
        return {"status": "not_found"}


# Global interview controller
interview_controller = InterviewController()
