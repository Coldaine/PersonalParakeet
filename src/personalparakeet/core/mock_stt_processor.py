#!/usr/bin/env python3
"""
Mock STT Processor - For testing and development when NeMo is not available
"""

import logging
import asyncio
import time
import numpy as np
from typing import Optional

from personalparakeet.config import V3Config

logger = logging.getLogger(__name__)


class MockSTTProcessor:
    """
    Mock Speech-to-Text processor for testing and development
    Returns placeholder text for any audio input
    """

    def __init__(self, config: V3Config):
        self.config = config
        self.is_initialized = False
        self.device = "cpu"  # Mock always uses CPU

        # Performance tracking (mock values)
        self.transcription_count = 0
        self.total_transcription_time = 0.0
        self.transcription_times = []

    async def initialize(self):
        """Initialize the mock STT processor"""
        try:
            logger.info("Initializing Mock STT Processor...")
            start_time = time.time()

            # Simulate some initialization time
            await asyncio.sleep(0.1)

            self.is_initialized = True
            load_time = time.time() - start_time
            logger.info(f"Mock STT Processor initialized in {load_time:.2f}s")

        except Exception as e:
            logger.error(f"Failed to initialize Mock STT processor: {e}")
            raise

    def transcribe(self, audio_chunk: np.ndarray) -> Optional[str]:
        """
        Mock transcribe audio chunk to text

        Args:
            audio_chunk: Audio data as numpy array (float32)

        Returns:
            Mock transcribed text
        """
        if not self.is_initialized:
            logger.error("Mock STT processor not initialized")
            return None

        try:
            # Simulate processing time
            start_time = time.time()

            # Check if audio chunk has enough energy (simple threshold)
            if np.max(np.abs(audio_chunk)) < 0.01:
                return None  # Silent audio

            # Mock transcription responses
            mock_responses = [
                "Hello world",
                "This is a test",
                "Mock transcription working",
                "PersonalParakeet is running",
                "Speech recognition active",
            ]

            # Return a mock response based on chunk properties
            response_index = (len(audio_chunk) // 1000) % len(mock_responses)
            text = mock_responses[response_index]

            # Track performance
            processing_time = time.time() - start_time
            self.transcription_count += 1
            self.total_transcription_time += processing_time
            self.transcription_times.append(processing_time)

            # Keep only last 100 times for rolling average
            if len(self.transcription_times) > 100:
                self.transcription_times.pop(0)

            logger.info(f"Mock transcription: '{text}' (processing: {processing_time*1000:.1f}ms)")
            return text

        except Exception as e:
            logger.error(f"Mock transcription failed: {e}")
            return None

    def get_performance_stats(self) -> dict:
        """Get mock performance statistics"""
        if not self.transcription_times:
            return {
                "total_transcriptions": 0,
                "avg_processing_time_ms": 0,
                "total_processing_time_s": 0,
            }

        avg_time = sum(self.transcription_times) / len(self.transcription_times)
        return {
            "total_transcriptions": self.transcription_count,
            "avg_processing_time_ms": avg_time * 1000,
            "total_processing_time_s": self.total_transcription_time,
            "last_100_avg_ms": avg_time * 1000,
        }

    def cleanup(self):
        """Cleanup mock resources"""
        logger.info("Mock STT Processor cleanup completed")
        self.is_initialized = False
