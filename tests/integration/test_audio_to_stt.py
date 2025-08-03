"""Test audio capture to STT pipeline."""

import queue
import threading
import time
from typing import Optional

import numpy as np
import pyaudio
import pytest
import torch
import whisper

from tests.core import BaseHardwareTest


class TestAudioToSTT(BaseHardwareTest):
    """Test audio capture to speech-to-text pipeline."""
    
    @pytest.mark.integration
    def test_basic_audio_to_stt_pipeline(self, audio_test_device):
        """Test basic audio capture and transcription."""
        # Load model
        model = whisper.load_model("base")
        
        # Setup audio capture
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=16000,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=audio_test_device,
            frames_per_buffer=1024
        )
        
        try:
            # Capture 2 seconds of audio
            print("\nCapturing 2 seconds of audio...")
            frames = []
            for _ in range(int(16000 * 2 / 1024)):
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)
            
            # Convert to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
            audio_float = audio_data.astype(np.float32) / 32768.0
            
            # Transcribe
            print("Transcribing...")
            result = model.transcribe(audio_float, language="en")
            
            print(f"Transcription: '{result['text']}'")
            
            # Verify result structure
            assert isinstance(result, dict)
            assert "text" in result
            assert "segments" in result
            
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
            del model
            if self.gpu_available:
                torch.cuda.empty_cache()
    
    @pytest.mark.integration
    def test_streaming_audio_transcription(self, audio_test_device):
        """Test streaming audio with chunked transcription."""
        model = whisper.load_model("base")
        
        # Setup audio
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=16000,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=audio_test_device,
            frames_per_buffer=1024
        )
        
        # Audio buffer
        audio_queue = queue.Queue()
        transcription_results = []
        
        def audio_capture_thread():
            """Capture audio in background."""
            try:
                for _ in range(50):  # ~3 seconds
                    data = stream.read(1024, exception_on_overflow=False)
                    audio_queue.put(data)
            except Exception as e:
                print(f"Audio capture error: {e}")
            finally:
                audio_queue.put(None)  # Signal end
        
        def transcription_thread():
            """Process audio chunks."""
            buffer = []
            chunk_size = 16000  # 1 second chunks
            
            while True:
                # Collect audio data
                while len(buffer) < chunk_size:
                    data = audio_queue.get()
                    if data is None:
                        break
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    buffer.extend(audio_data)
                
                if len(buffer) >= chunk_size or (data is None and buffer):
                    # Process chunk
                    chunk = np.array(buffer[:chunk_size], dtype=np.float32) / 32768.0
                    buffer = buffer[chunk_size:]
                    
                    # Transcribe
                    result = model.transcribe(chunk, language="en")
                    if result["text"].strip():
                        transcription_results.append(result["text"])
                
                if data is None:
                    break
        
        # Start threads
        capture_thread = threading.Thread(target=audio_capture_thread)
        transcribe_thread = threading.Thread(target=transcription_thread)
        
        try:
            print("\nStarting streaming transcription...")
            capture_thread.start()
            transcribe_thread.start()
            
            capture_thread.join()
            transcribe_thread.join()
            
            print(f"Transcribed {len(transcription_results)} chunks")
            for i, text in enumerate(transcription_results):
                print(f"  Chunk {i+1}: '{text}'")
            
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
            del model
            if self.gpu_available:
                torch.cuda.empty_cache()
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_continuous_pipeline_stability(self, audio_test_device):
        """Test continuous audio capture and transcription stability."""
        model = whisper.load_model("tiny")  # Use tiny for speed
        
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=16000,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=audio_test_device,
            frames_per_buffer=1024
        )
        
        try:
            print("\nRunning continuous pipeline for 10 seconds...")
            start_time = time.time()
            transcriptions = 0
            errors = 0
            
            while time.time() - start_time < 10.0:
                try:
                    # Capture 1 second
                    frames = []
                    for _ in range(16):
                        data = stream.read(1024, exception_on_overflow=False)
                        frames.append(data)
                    
                    # Convert and transcribe
                    audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
                    audio_float = audio_data.astype(np.float32) / 32768.0
                    
                    result = model.transcribe(audio_float, language="en")
                    transcriptions += 1
                    
                except Exception as e:
                    errors += 1
                    print(f"Pipeline error: {e}")
            
            duration = time.time() - start_time
            
            print(f"\nPipeline results:")
            print(f"  Duration: {duration:.1f}s")
            print(f"  Transcriptions: {transcriptions}")
            print(f"  Errors: {errors}")
            print(f"  Rate: {transcriptions/duration:.1f} transcriptions/sec")
            
            assert errors == 0, f"Pipeline errors occurred: {errors}"
            assert transcriptions > 8, f"Too few transcriptions: {transcriptions}"
            
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
            del model
            if self.gpu_available:
                torch.cuda.empty_cache()
    
    @pytest.mark.integration
    def test_audio_quality_impact(self, audio_test_device):
        """Test impact of audio quality on transcription."""
        model = whisper.load_model("base")
        
        # Generate test audio with speech-like characteristics
        sample_rate = 16000
        duration = 2.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create synthetic "speech" (modulated noise)
        base_audio = np.sin(2 * np.pi * 200 * t) * np.sin(2 * np.pi * 3 * t)
        base_audio += np.random.randn(len(t)) * 0.1
        
        # Test different audio conditions
        conditions = [
            ("clean", base_audio),
            ("noisy", base_audio + np.random.randn(len(t)) * 0.5),
            ("quiet", base_audio * 0.1),
            ("loud", base_audio * 2.0),
            ("clipped", np.clip(base_audio * 5.0, -1.0, 1.0)),
        ]
        
        results = {}
        for condition_name, audio in conditions:
            # Normalize
            audio = audio.astype(np.float32)
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio))
            
            # Transcribe
            result = model.transcribe(audio, language="en")
            results[condition_name] = result
            
            print(f"\n{condition_name} audio: '{result['text'][:50]}...'")
        
        # All conditions should produce some result
        for condition_name, result in results.items():
            assert isinstance(result, dict), f"{condition_name}: Invalid result"
            assert "text" in result, f"{condition_name}: No text in result"
        
        del model
        if self.gpu_available:
            torch.cuda.empty_cache()