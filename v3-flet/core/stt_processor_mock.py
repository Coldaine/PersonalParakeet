"""
Mock STT Processor for testing without PyTorch/NeMo
Simulates transcription for UI and pipeline testing
"""

import time
import random
import logging
import numpy as np
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class MockSTTProcessor:
    """Mock STT processor that simulates transcription"""
    
    def __init__(self, config):
        self.config = config
        self.sample_rate = 16000
        self.is_loaded = False
        self.transcription_count = 0
        
        # Simulated test phrases
        self.test_phrases = [
            "Hello from PersonalParakeet",
            "This is a test transcription",
            "The quick brown fox jumps over the lazy dog",
            "Testing voice activity detection",
            "Real-time speech recognition simulation",
            "Clarity engine will enhance this text",
        ]
        
        logger.info("MockSTTProcessor initialized (no model loaded)")
    
    async def initialize(self):
        """Initialize the mock STT processor"""
        logger.info("Initializing MockSTTProcessor...")
        self.load_model()
        logger.info("MockSTTProcessor initialized successfully")
    
    def load_model(self):
        """Simulate model loading"""
        logger.info("Loading mock STT model...")
        time.sleep(0.5)  # Simulate loading delay
        self.is_loaded = True
        logger.info("Mock STT model 'loaded' successfully")
        return True
    
    def transcribe(self, audio_chunk: np.ndarray) -> Tuple[str, float]:
        """
        Simulate transcription based on audio energy
        
        Returns:
            Tuple of (transcribed_text, confidence)
        """
        if not self.is_loaded:
            logger.warning("Model not loaded, cannot transcribe")
            return "", 0.0
        
        # Calculate audio energy
        energy = np.sqrt(np.mean(audio_chunk**2))
        
        # If energy is above threshold, return a test phrase
        if energy > 0.01:  # Voice detected
            self.transcription_count += 1
            
            # Pick a phrase based on count
            phrase_index = self.transcription_count % len(self.test_phrases)
            text = self.test_phrases[phrase_index]
            
            # Add some variation
            if random.random() > 0.7:
                text = text.lower()
            
            confidence = 0.85 + random.random() * 0.15  # 85-100% confidence
            
            logger.debug(f"Mock transcription #{self.transcription_count}: '{text}' (confidence: {confidence:.2f})")
            return text, confidence
        
        return "", 0.0
    
    def process_audio_chunk(self, audio_chunk: np.ndarray) -> Optional[str]:
        """Process audio chunk and return transcription if any"""
        text, confidence = self.transcribe(audio_chunk)
        
        if text and confidence > 0.5:
            return text
        return None
    
    def get_status(self) -> dict:
        """Get processor status"""
        return {
            'loaded': self.is_loaded,
            'model_name': 'MockSTT-v1',
            'sample_rate': self.sample_rate,
            'transcription_count': self.transcription_count,
            'mode': 'simulation'
        }
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("MockSTTProcessor cleanup complete")
        self.is_loaded = False


# For drop-in replacement
STTProcessor = MockSTTProcessor