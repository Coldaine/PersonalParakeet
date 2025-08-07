#!/usr/bin/env python3
"""
Full pipeline test for PersonalParakeet v3
Tests audio capture → mock STT → clarity engine → text injection
"""

import asyncio
import logging
import time
from pathlib import Path

import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Import components
from personalparakeet.audio_engine import AudioEngine
from personalparakeet.config import V3Config
from personalparakeet.core.clarity_engine import ClarityEngine
from personalparakeet.core.injection_manager_enhanced import EnhancedInjectionManager

# Create injection manager instance
injection_manager = EnhancedInjectionManager()


def test_clarity_engine():
    """Test clarity engine corrections"""
    print("\n=== Testing Clarity Engine ===")

    engine = ClarityEngine(enable_rule_based=True)  # Rule-based mode

    test_cases = [
        "hello world",
        "i am going to teh store",
        "python programing is fun",
        "the whether is nice today",
    ]

    for text in test_cases:
        result = engine.correct_text_sync(text)
        print(f"Input:  '{text}'")
        print(f"Output: '{result.corrected_text}'")
        if result.corrections_made:
            print(f"Corrections: {result.corrections_made}")
        print()

    engine.stop_worker()
    print("✓ Clarity Engine test complete")


def test_injection_pipeline():
    """Test text injection"""
    print("\n=== Testing Text Injection ===")

    # Get current app info
    app_info = injection_manager.get_current_application()
    if app_info:
        print(f"Current app: {app_info.name} ({app_info.app_type.name})")

    # Test injection
    test_text = "Hello from PersonalParakeet v3!"
    print(f"Injecting: '{test_text}'")

    success = injection_manager.inject_text(test_text)
    print(f"Result: {'✓ Success' if success else '✗ Failed'}")

    # Get stats
    stats = injection_manager.get_performance_stats()
    print(f"\nInjection stats:")
    print(f"  Total: {stats['total_injections']}")
    print(f"  Success rate: {stats['success_rate_percent']}%")
    print(f"  Average time: {stats['average_injection_time_ms']}ms")


async def test_audio_pipeline():
    """Test audio capture and processing pipeline"""
    print("\n=== Testing Audio Pipeline ===")

    config = V3Config()
    # Force mock STT for testing
    config.audio.use_mock_stt = True
    engine = AudioEngine(config, asyncio.get_event_loop())

    # Track callbacks
    transcriptions = []
    corrections = []

    def on_raw(text):
        transcriptions.append(text)
        print(f"[STT] '{text}'")

    def on_corrected(result):
        corrections.append(result)
        print(f"[Clarity] '{result.corrected_text}'")

    engine.set_raw_transcription_callback(on_raw)
    engine.set_corrected_transcription_callback(on_corrected)

    # Initialize and start
    await engine.initialize()
    await engine.start()

    print("Audio pipeline running for 10 seconds...")
    print("Speak into your microphone to test transcription!")

    # Run for 10 seconds
    await asyncio.sleep(10)

    # Stop engine
    await engine.stop()

    print(f"\nResults:")
    print(f"  Transcriptions: {len(transcriptions)}")
    print(f"  Corrections: {len(corrections)}")

    if transcriptions:
        print("\nSample transcriptions:")
        for text in transcriptions[-3:]:
            print(f"  - {text}")


def simulate_audio_with_injection():
    """Simulate audio input and test injection"""
    print("\n=== Simulating Full Pipeline ===")

    # Simulate audio detection
    print("1. Simulating voice detection...")
    time.sleep(0.5)

    # Simulate transcription
    text = "This is a test of the full pipeline"
    print(f"2. Mock STT transcribed: '{text}'")
    time.sleep(0.5)

    # Apply clarity
    engine = ClarityEngine(enable_rule_based=True)
    result = engine.correct_text_sync(text)
    print(f"3. Clarity corrected: '{result.corrected_text}'")
    time.sleep(0.5)

    # Simulate pause detection
    print("4. Pause detected - auto-committing...")
    time.sleep(0.5)

    # Inject text
    success = injection_manager.inject_text(result.corrected_text)
    print(f"5. Injection: {'✓ Success' if success else '✗ Failed'}")

    engine.stop_worker()
    print("\n✓ Full pipeline simulation complete!")


def main():
    """Run all pipeline tests"""
    print("PersonalParakeet v3 - Full Pipeline Test")
    print("=" * 50)

    try:
        # Test individual components
        test_clarity_engine()
        test_injection_pipeline()

        # Test audio pipeline
        print("\nRunning audio pipeline test...")
        asyncio.run(test_audio_pipeline())

        # Simulate full flow
        simulate_audio_with_injection()

        print("\n" + "=" * 50)
        print("✓ All pipeline tests completed!")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
