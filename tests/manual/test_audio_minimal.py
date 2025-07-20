# test_audio_minimal.py
# Windows Audio Debugging Script for Parakeet Dictation Project

import sounddevice as sd
import numpy as np

def test_windows_audio():
    """Test basic audio capture on Windows"""
    print("=== Windows Audio Test ===")
    
    # List available devices
    print("\nAvailable audio devices:")
    devices = sd.query_devices()
    print(devices)
    
    # Test basic capture
    print(f"\nTesting 5-second audio capture at 16kHz...")
    duration = 5
    sample_rate = 16000
    
    try:
        audio = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype=np.float32)
        sd.wait()
        
        print(f"[PASS] Successfully captured {len(audio)} samples")
        print(f"STATS: Audio level: {np.max(np.abs(audio)):.3f}")
        
        if np.max(np.abs(audio)) > 0.001:
            print("SUCCESS: Audio detected - microphone is working!")
        else:
            print("[FAIL] No audio detected - check microphone permissions")
            
        return audio
        
    except Exception as e:
        print(f"[FAIL] Audio capture failed: {e}")
        return None

if __name__ == "__main__":
    test_windows_audio()
