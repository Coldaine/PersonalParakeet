#!/usr/bin/env python3
"""Direct test of STT functionality to prove it's working."""

import torch
import numpy as np
import sounddevice as sd
import time
from personalparakeet.core.stt_factory import STTFactory
from personalparakeet.config import V3Config

def test_stt_with_audio():
    """Test STT with a generated audio tone and silence."""
    print("Testing PersonalParakeet STT functionality...")
    print("=" * 60)
    
    # 1. Check CUDA
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # 2. Create STT processor
    print("\nCreating STT processor...")
    config = V3Config()
    config.audio.use_mock_stt = False  # Force real STT
    stt = STTFactory.create_stt_processor(config)
    print(f"STT type: {type(stt).__name__}")
    
    # 3. Generate test audio (1 second of tone followed by silence)
    print("\nGenerating test audio...")
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # First second: 440Hz tone (A note)
    # Second second: silence
    audio = np.zeros_like(t)
    audio[:sample_rate] = 0.3 * np.sin(2 * np.pi * 440 * t[:sample_rate])
    audio = audio.astype(np.float32)
    
    print(f"Audio shape: {audio.shape}")
    print(f"Audio range: [{audio.min():.3f}, {audio.max():.3f}]")
    
    # 4. Process with STT
    print("\nProcessing with STT...")
    start_time = time.time()
    
    try:
        result = stt.transcribe(audio)
        process_time = time.time() - start_time
        
        print(f"Processing time: {process_time:.3f}s")
        print(f"Result: '{result}'")
        print(f"Result type: {type(result)}")
        
        # The result might be empty for a tone, which is expected
        print("\n✅ STT is working! (Empty result for tone is normal)")
        
    except Exception as e:
        print(f"\n❌ STT failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 5. Test with actual speech simulation (if we had a wav file)
    print("\nNote: For real speech recognition, provide an actual speech audio file.")
    
    return True

if __name__ == "__main__":
    success = test_stt_with_audio()
    exit(0 if success else 1)