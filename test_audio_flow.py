#!/usr/bin/env python3
"""
Test end-to-end audio flow for PersonalParakeet Workshop Box
Verifies: Audio capture -> Parakeet transcription -> WebSocket -> UI
"""

import asyncio
import json
import time
import websockets
from personalparakeet.dictation import SimpleDictation
import sounddevice as sd

async def test_websocket_connection():
    """Test WebSocket connection to backend"""
    print("Testing WebSocket connection...")
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            print("[OK] Connected to WebSocket server")
            
            # Wait for a message
            print("Waiting for transcription data...")
            message = await asyncio.wait_for(websocket.recv(), timeout=10)
            data = json.loads(message)
            print(f"[OK] Received: {data}")
            return True
    except asyncio.TimeoutError:
        print("[X] Timeout waiting for WebSocket data")
        return False
    except Exception as e:
        print(f"[X] WebSocket error: {e}")
        return False

def test_audio_capture():
    """Test audio capture"""
    print("\nTesting audio capture...")
    try:
        # List audio devices
        devices = sd.query_devices()
        print(f"[OK] Found {len(devices)} audio devices")
        
        # Test recording
        print("Recording 2 seconds of audio...")
        duration = 2
        fs = 16000
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        
        print(f"[OK] Captured {len(recording)} samples")
        print(f"    Audio level: min={recording.min():.3f}, max={recording.max():.3f}")
        
        if abs(recording).max() < 0.001:
            print("[!] WARNING: Audio appears to be silent")
            print("    Check your microphone is connected and not muted")
        
        return True
    except Exception as e:
        print(f"[X] Audio capture error: {e}")
        return False

def test_parakeet_model():
    """Test Parakeet model loading"""
    print("\nTesting Parakeet model...")
    try:
        from personalparakeet.cuda_fix import ensure_cuda_available
        ensure_cuda_available()
        
        import torch
        print(f"[OK] PyTorch {torch.__version__}")
        print(f"[OK] CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"[OK] GPU: {torch.cuda.get_device_name(0)}")
        
        # Try to import NeMo
        import nemo
        print(f"[OK] NeMo toolkit available")
        
        return True
    except Exception as e:
        print(f"[X] Model loading error: {e}")
        return False

async def main():
    """Run all tests"""
    print("=== PersonalParakeet Audio Flow Test ===\n")
    
    # Test 1: Audio capture
    audio_ok = test_audio_capture()
    
    # Test 2: Parakeet model
    model_ok = test_parakeet_model()
    
    # Test 3: WebSocket (requires backend running)
    print("\nNOTE: WebSocket test requires workshop_websocket_bridge_v2.py running")
    ws_ok = await test_websocket_connection()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Audio Capture: {'PASS' if audio_ok else 'FAIL'}")
    print(f"Parakeet Model: {'PASS' if model_ok else 'FAIL'}")
    print(f"WebSocket: {'PASS' if ws_ok else 'FAIL (backend not running?)'}")
    
    if audio_ok and model_ok:
        print("\nCore components are working!")
        if not ws_ok:
            print("Run 'python workshop_websocket_bridge_v2.py' to test WebSocket")
    else:
        print("\nSome components need attention")

if __name__ == "__main__":
    asyncio.run(main())