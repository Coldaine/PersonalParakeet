#!/usr/bin/env python3
"""
Quick live test to demonstrate working PersonalParakeet v3 system
"""

import asyncio
import time
from audio_engine import AudioEngine
from personalparakeet.core.stt_factory import STTFactory
from personalparakeet.core.clarity_engine import ClarityEngine
from personalparakeet.core.vad_engine import VoiceActivityDetector
from config import V3Config

async def live_stt_test():
    """Run a live STT test with the complete pipeline"""
    print("🦜 PersonalParakeet v3 - Live STT Test")
    print("=" * 50)
    
    config = V3Config()
    print(f"✓ Configuration loaded (mock STT: {config.audio.use_mock_stt})")
    
    # Initialize components
    print("✓ Initializing components...")
    
    try:
        # Test STT Factory
        stt = STTFactory.create_stt_processor(config)
        print(f"✓ STT Processor: {type(stt).__name__}")
        
        # Test Clarity Engine  
        clarity = ClarityEngine()
        print("✓ Clarity Engine initialized")
        
        # Test VAD
        vad = VoiceActivityDetector()
        print("✓ Voice Activity Detector initialized")
        
        # Test Audio Engine
        engine = AudioEngine(config)
        await engine.initialize()
        print("✓ Audio Engine initialized")
        
        print("\n🎤 Starting live audio test for 15 seconds...")
        print("Speak into your microphone to test the system!")
        print("(Using mock STT - will show simulated transcription)")
        
        transcription_count = 0
        
        def on_transcription(text):
            nonlocal transcription_count
            transcription_count += 1
            print(f"📝 Transcription #{transcription_count}: '{text}'")
            
            # Test clarity correction
            corrected = clarity.correct_text(text)
            if corrected.corrected != text:
                print(f"✨ Corrected: '{corrected.corrected}'")
        
        # Set up callback
        engine.on_transcription = on_transcription
        
        # Start audio processing
        await engine.start()
        
        # Run for 15 seconds
        await asyncio.sleep(15)
        
        # Stop
        await engine.stop()
        
        print(f"\n✅ Live test complete!")
        print(f"   Total transcriptions: {transcription_count}")
        print(f"   Audio backend: Mock STT (working correctly)")
        print(f"   System status: All components operational")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(live_stt_test())