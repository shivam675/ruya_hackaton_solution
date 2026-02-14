"""
Text-to-Speech Service using Kokoro
"""
from kokoro import KPipeline
import sounddevice as sd
import numpy as np
import logging
from typing import Optional
import io

logger = logging.getLogger(__name__)


class TTSService:
    """Kokoro Text-to-Speech Service"""
    
    def __init__(self, voice: str = "af_bella", sample_rate: int = 24000):
        self.pipeline: Optional[KPipeline] = None
        self.voice = voice
        self.sample_rate = sample_rate
        logger.info("TTS Service initialized")
    
    def initialize(self):
        """Initialize Kokoro pipeline"""
        if not self.pipeline:
            logger.info("🔊 Initializing Kokoro TTS pipeline...")
            self.pipeline = KPipeline(lang_code='a')
            logger.info("✅ TTS pipeline ready")
    
    def synthesize_and_play(self, text: str) -> bool:
        """
        Synthesize text to speech and play it
        
        Args:
            text: Text to synthesize
            
        Returns:
            True if successful
        """
        if not self.pipeline:
            self.initialize()
        
        try:
            logger.info(f"🔊 Speaking: {text[:50]}...")
            
            generator = self.pipeline(text, voice=self.voice)
            
            # Play all audio chunks
            for i, (gs, ps, audio) in enumerate(generator):
                sd.play(audio, samplerate=self.sample_rate)
                sd.wait()
            
            logger.info("✅ Speech completed")
            return True
            
        except Exception as e:
            logger.error(f"❌ TTS error: {e}")
            return False
    
    def synthesize_to_bytes(self, text: str) -> Optional[bytes]:
        """
        Synthesize text to audio bytes (for WebSocket streaming)
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio bytes or None
        """
        if not self.pipeline:
            self.initialize()
        
        try:
            generator = self.pipeline(text, voice=self.voice)
            
            # Collect all audio chunks
            audio_chunks = []
            for i, (gs, ps, audio) in enumerate(generator):
                audio_chunks.append(audio)
            
            if audio_chunks:
                # Concatenate all chunks
                full_audio = np.concatenate(audio_chunks)
                # Convert to bytes
                return full_audio.tobytes()
            
            return None
            
        except Exception as e:
            logger.error(f"❌ TTS synthesis error: {e}")
            return None


# Global TTS service
tts_service = TTSService()
