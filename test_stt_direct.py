#!/usr/bin/env python3
"""Direct test of STT functionality"""

import asyncio
import numpy as np
import sounddevice as sd
import logging

from personalparakeet.config import V3Config
from personalparakeet.core.stt_factory import STTFactory

logging.basicConfig(level=logging.INFO)

async def test_stt():
    """Test STT directly with microphone input"""
    print("=== Direct STT Test ===")
    
    # Create config
    config = V3Config()
    config.audio.use_mock_stt = False  # Use real STT
    
    # Create STT processor
    print("Creating STT processor...")
    stt = STTFactory.create_stt_processor(config)
    
    print("Initializing STT...")
    await stt.initialize()
    print("STT initialized!")
    
    # Record 3 seconds of audio
    print("\nSpeak now for 3 seconds...")
    duration = 3.0
    sample_rate = 16000
    
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype='float32')
    sd.wait()
    
    print("Processing audio...")
    audio = recording.flatten()
    
    # Transcribe
    result = stt.transcribe(audio)
    
    print(f"\nTranscription result: '{result}'")
    
    if result:
        print("✅ STT is working!")
    else:
        print("❌ No transcription received")

if __name__ == "__main__":
    asyncio.run(test_stt())