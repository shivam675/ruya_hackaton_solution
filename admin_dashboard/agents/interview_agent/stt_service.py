"""
Speech-to-Text Service using RealtimeSTT
"""
from RealtimeSTT import AudioToTextRecorder
import logging
from typing import Callable, Optional
import asyncio

logger = logging.getLogger(__name__)


class STTService:
    """Real-time Speech-to-Text Service"""
    
    def __init__(self):
        self.recorder: Optional[AudioToTextRecorder] = None
        self.is_listening = False
        logger.info("STT Service initialized")
    
    def initialize(self):
        """Initialize the STT recorder"""
        if not self.recorder:
            logger.info("🎤 Initializing STT recorder...")
            self.recorder = AudioToTextRecorder()
            logger.info("✅ STT recorder ready")
    
    async def start_listening(self, callback: Callable[[str], None]):
        """
        Start listening for speech
        
        Args:
            callback: Function to call with transcribed text
        """
        if not self.recorder:
            self.initialize()
        
        self.is_listening = True
        logger.info("🎤 Started listening...")
        
        # This blocks until speech is detected
        # In async context, we run this in executor
        def listen():
            while self.is_listening:
                try:
                    self.recorder.text(callback)
                except Exception as e:
                    logger.error(f"❌ STT error: {e}")
                    break
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, listen)
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        logger.info("🛑 Stopped listening")
    
    def transcribe_audio(self, audio_data: bytes) -> str:
        """
        Transcribe audio data
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Transcribed text
        """
        # Placeholder - implement actual transcription
        logger.info("🎤 Transcribing audio...")
        return "Transcribed text placeholder"


# Global STT service
stt_service = STTService()
