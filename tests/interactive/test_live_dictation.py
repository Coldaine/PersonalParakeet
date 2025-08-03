"""Interactive tests for live dictation."""

import time

import numpy as np
import pyaudio
import pytest
import whisper

from tests.core import BaseHardwareTest


class TestLiveDictation(BaseHardwareTest):
    """Interactive tests requiring human speech input."""
    
    @pytest.mark.interactive
    def test_live_speech_recognition(self, audio_test_device):
        """Test live speech recognition with human input."""
        print("\n" + "="*60)
        print("INTERACTIVE TEST: Live Speech Recognition")
        print("="*60)
        print("\nThis test requires you to speak into your microphone.")
        print("Please read the following phrases when prompted:")
        print("1. 'Hello, this is a test'")
        print("2. 'The quick brown fox jumps over the lazy dog'")
        print("3. Count from one to ten")
        print("\nPress Enter when ready to begin...")
        input()
        
        model = whisper.load_model("base")
        pa = pyaudio.PyAudio()
        
        test_phrases = [
            ("Test 1", "Please say: 'Hello, this is a test'", 3),
            ("Test 2", "Please say: 'The quick brown fox jumps over the lazy dog'", 5),
            ("Test 3", "Please count from one to ten", 5)
        ]
        
        results = []
        
        try:
            for test_name, prompt, duration in test_phrases:
                print(f"\n{test_name}: {prompt}")
                print(f"Recording for {duration} seconds in 3...")
                time.sleep(1)
                print("2...")
                time.sleep(1)
                print("1...")
                time.sleep(1)
                print("Recording! Speak now...")
                
                # Record audio
                stream = pa.open(
                    rate=16000,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    input_device_index=audio_test_device,
                    frames_per_buffer=1024
                )
                
                frames = []
                for _ in range(int(16000 * duration / 1024)):
                    data = stream.read(1024)
                    frames.append(data)
                
                stream.stop_stream()
                stream.close()
                
                print("Processing...")
                
                # Convert and transcribe
                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                audio_float = audio_data.astype(np.float32) / 32768.0
                
                result = model.transcribe(audio_float, language="en")
                transcribed_text = result["text"].strip()
                
                results.append({
                    "test": test_name,
                    "transcription": transcribed_text,
                    "duration": duration
                })
                
                print(f"Transcribed: '{transcribed_text}'")
                
                # Let user verify
                response = input("Does this look correct? (y/n): ").lower()
                results[-1]["verified"] = response == 'y'
        
        finally:
            pa.terminate()
            del model
        
        # Summary
        print("\n" + "="*60)
        print("Test Summary:")
        print("="*60)
        for result in results:
            status = "✓" if result.get("verified") else "✗"
            print(f"{status} {result['test']}: '{result['transcription']}'")
        
        verified_count = sum(1 for r in results if r.get("verified"))
        print(f"\nVerified: {verified_count}/{len(results)}")
        
        assert verified_count > 0, "No transcriptions were verified as correct"
    
    @pytest.mark.interactive
    def test_continuous_dictation(self, audio_test_device):
        """Test continuous dictation mode."""
        print("\n" + "="*60)
        print("INTERACTIVE TEST: Continuous Dictation")
        print("="*60)
        print("\nThis test will continuously transcribe your speech.")
        print("Speak naturally and observe the transcriptions.")
        print("Say 'stop recording' to end the test.")
        print("\nPress Enter to begin...")
        input()
        
        model = whisper.load_model("base")
        pa = pyaudio.PyAudio()
        
        stream = pa.open(
            rate=16000,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=audio_test_device,
            frames_per_buffer=1024
        )
        
        transcriptions = []
        stop_phrase_detected = False
        
        try:
            print("\nListening... (say 'stop recording' to end)")
            buffer = []
            
            while not stop_phrase_detected:
                # Capture 2 seconds of audio
                for _ in range(32):
                    data = stream.read(1024, exception_on_overflow=False)
                    buffer.append(data)
                
                # Convert and transcribe
                audio_data = np.frombuffer(b''.join(buffer), dtype=np.int16)
                audio_float = audio_data.astype(np.float32) / 32768.0
                
                # Clear buffer but keep last 0.5 seconds for continuity
                buffer = buffer[-8:]
                
                result = model.transcribe(audio_float, language="en")
                text = result["text"].strip()
                
                if text:
                    print(f"→ {text}")
                    transcriptions.append(text)
                    
                    # Check for stop phrase
                    if "stop recording" in text.lower():
                        stop_phrase_detected = True
                        print("\nStop phrase detected!")
        
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
            del model
        
        print(f"\nTotal transcriptions: {len(transcriptions)}")
        assert len(transcriptions) > 0, "No transcriptions captured"
        assert stop_phrase_detected, "Stop phrase was not detected"
    
    @pytest.mark.interactive
    def test_noise_handling(self, audio_test_device):
        """Test speech recognition with background noise."""
        print("\n" + "="*60)
        print("INTERACTIVE TEST: Noise Handling")
        print("="*60)
        print("\nThis test evaluates speech recognition with background noise.")
        print("We'll test in different conditions:")
        print("1. Quiet environment")
        print("2. With background music/TV")
        print("3. While typing on keyboard")
        print("\nPress Enter to begin...")
        input()
        
        model = whisper.load_model("base")
        pa = pyaudio.PyAudio()
        
        conditions = [
            ("Quiet", "Please speak in a quiet environment"),
            ("Background noise", "Please play some music or TV in the background"),
            ("Typing", "Please type on your keyboard while speaking")
        ]
        
        results = []
        test_phrase = "The weather is nice today"
        
        try:
            for condition_name, instruction in conditions:
                print(f"\n{condition_name} test:")
                print(instruction)
                print(f"When ready, say: '{test_phrase}'")
                input("Press Enter when ready...")
                
                print("Recording for 3 seconds...")
                
                stream = pa.open(
                    rate=16000,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    input_device_index=audio_test_device,
                    frames_per_buffer=1024
                )
                
                frames = []
                for _ in range(int(16000 * 3 / 1024)):
                    data = stream.read(1024)
                    frames.append(data)
                
                stream.stop_stream()
                stream.close()
                
                # Analyze audio
                audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                audio_float = audio_data.astype(np.float32) / 32768.0
                
                # Calculate noise level
                rms = np.sqrt(np.mean(audio_float**2))
                
                # Transcribe
                result = model.transcribe(audio_float, language="en")
                text = result["text"].strip()
                
                results.append({
                    "condition": condition_name,
                    "transcription": text,
                    "noise_level": rms,
                    "expected": test_phrase
                })
                
                print(f"Transcribed: '{text}'")
                print(f"Noise level: {rms:.4f}")
        
        finally:
            pa.terminate()
            del model
        
        # Summary
        print("\n" + "="*60)
        print("Noise Handling Summary:")
        print("="*60)
        for result in results:
            match = result["expected"].lower() in result["transcription"].lower()
            status = "✓" if match else "✗"
            print(f"{status} {result['condition']}:")
            print(f"   Transcription: '{result['transcription']}'")
            print(f"   Noise level: {result['noise_level']:.4f}")
        
        # At least the quiet condition should work
        quiet_result = next(r for r in results if r["condition"] == "Quiet")
        assert quiet_result["expected"].lower() in quiet_result["transcription"].lower(), \
            "Failed to transcribe correctly in quiet environment"