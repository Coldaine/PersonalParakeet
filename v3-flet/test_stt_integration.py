#!/usr/bin/env python3
"""
Test script to verify STT integration in v3
Tests the real NeMo Parakeet model integration
"""

import asyncio
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from core.stt_processor import STTProcessor
from config import V3Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_stt_integration():
    """Test STT processor initialization and basic functionality"""
    logger.info("Testing STT Integration...")
    
    try:
        # Initialize config
        config = V3Config()
        
        # Initialize STT processor
        logger.info("Initializing STT Processor...")
        stt = STTProcessor(config)
        await stt.initialize()
        logger.info("✓ STT Processor initialized successfully")
        
        # Test with dummy audio
        import numpy as np
        sample_rate = 16000
        duration = 1.0
        
        # Generate test audio (sine wave)
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
        
        logger.info("Testing transcription...")
        result = stt.transcribe_sync(audio)
        logger.info(f"Transcription result: '{result}'")
        
        # Cleanup
        await stt.cleanup()
        logger.info("✓ Cleanup successful")
        
        logger.info("\n✓ STT Integration test PASSED!")
        return True
        
    except Exception as e:
        logger.error(f"✗ STT Integration test FAILED: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = asyncio.run(test_stt_integration())
    sys.exit(0 if success else 1)