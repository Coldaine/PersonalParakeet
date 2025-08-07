#!/usr/bin/env python3
"""Direct STT test to debug transcription issues"""

import asyncio
import logging

import numpy as np

from personalparakeet.config import V3Config
from personalparakeet.core.stt_factory import STTFactory

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_stt():
    """Test STT directly with a simple audio chunk"""
    try:
        # Create config
        config = V3Config()

        # Create STT processor
        logger.info("Creating STT processor...")
        stt_processor = STTFactory.create_stt_processor(config)

        # Initialize
        logger.info("Initializing STT processor...")
        await stt_processor.initialize()

        # Create test audio chunk (1 second of sine wave at 440Hz)
        logger.info("Creating test audio...")
        duration = 1.0  # seconds
        sample_rate = config.audio.model_sample_rate  # 16000
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440  # A4 note
        audio_chunk = (0.3 * np.sin(2 * np.pi * frequency * t)).astype(np.float32)

        logger.info(f"Test audio shape: {audio_chunk.shape}, dtype: {audio_chunk.dtype}")
        logger.info(f"Audio max amplitude: {np.max(np.abs(audio_chunk)):.4f}")

        # Try to transcribe
        logger.info("Calling transcribe()...")
        result = stt_processor.transcribe(audio_chunk)
        logger.info(f"Transcription result: {result}")

        # Try with silence (should return None)
        logger.info("Testing with silence...")
        silence = np.zeros(int(sample_rate * 0.5), dtype=np.float32)
        result = stt_processor.transcribe(silence)
        logger.info(f"Silence transcription result: {result}")

        # Cleanup
        await stt_processor.cleanup()
        logger.info("Test completed")

    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(test_stt())
