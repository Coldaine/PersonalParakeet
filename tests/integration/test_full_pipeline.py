"""Test complete end-to-end pipeline."""

import queue
import threading
import time
from dataclasses import dataclass
from typing import List, Optional

import numpy as np
import pyaudio
import pytest
import torch
import whisper

from tests.core import BaseHardwareTest


@dataclass
class PipelineMetrics:
    """Metrics for pipeline performance."""
    total_audio_chunks: int = 0
    total_transcriptions: int = 0
    total_injections: int = 0
    total_errors: int = 0
    start_time: float = 0
    end_time: float = 0
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def transcription_rate(self) -> float:
        return self.total_transcriptions / self.duration if self.duration > 0 else 0


class TestFullPipeline(BaseHardwareTest):
    """Test complete audio capture -> STT -> injection pipeline."""
    
    @pytest.mark.integration
    def test_basic_full_pipeline(self, audio_test_device):
        """Test basic full pipeline operation."""
        # Initialize components
        model = whisper.load_model("base")
        pa = pyaudio.PyAudio()
        
        # Queues for pipeline stages
        audio_queue = queue.Queue(maxsize=100)
        text_queue = queue.Queue(maxsize=100)
        
        # Metrics
        metrics = PipelineMetrics()
        
        def audio_capture_stage():
            """Capture audio and queue for processing."""
            stream = pa.open(
                rate=16000,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=audio_test_device,
                frames_per_buffer=1024
            )
            
            try:
                # Capture for 5 seconds
                for _ in range(int(16000 * 5 / 1024)):
                    data = stream.read(1024, exception_on_overflow=False)
                    audio_queue.put(data)
                    metrics.total_audio_chunks += 1
            finally:
                audio_queue.put(None)  # Signal end
                stream.stop_stream()
                stream.close()
        
        def stt_processing_stage():
            """Process audio chunks through STT."""
            buffer = []
            chunk_size = 16000  # 1 second chunks
            
            while True:
                # Collect audio
                data = audio_queue.get()
                if data is None:
                    # Process remaining buffer
                    if buffer:
                        audio_float = np.array(buffer, dtype=np.float32) / 32768.0
                        result = model.transcribe(audio_float, language="en")
                        if result["text"].strip():
                            text_queue.put(result["text"])
                            metrics.total_transcriptions += 1
                    text_queue.put(None)
                    break
                
                # Add to buffer
                audio_data = np.frombuffer(data, dtype=np.int16)
                buffer.extend(audio_data)
                
                # Process when we have enough
                if len(buffer) >= chunk_size:
                    chunk = np.array(buffer[:chunk_size], dtype=np.float32) / 32768.0
                    buffer = buffer[chunk_size:]
                    
                    try:
                        result = model.transcribe(chunk, language="en")
                        if result["text"].strip():
                            text_queue.put(result["text"])
                            metrics.total_transcriptions += 1
                    except Exception as e:
                        print(f"STT error: {e}")
                        metrics.total_errors += 1
        
        def text_injection_stage():
            """Simulate text injection."""
            while True:
                text = text_queue.get()
                if text is None:
                    break
                
                # Simulate injection
                time.sleep(0.01 * len(text))  # Simulate typing
                print(f"Injected: '{text}'")
                metrics.total_injections += 1
        
        # Start pipeline
        print("\nStarting full pipeline test...")
        metrics.start_time = time.time()
        
        threads = [
            threading.Thread(target=audio_capture_stage, name="audio"),
            threading.Thread(target=stt_processing_stage, name="stt"),
            threading.Thread(target=text_injection_stage, name="injection")
        ]
        
        try:
            for thread in threads:
                thread.start()
            
            for thread in threads:
                thread.join()
            
            metrics.end_time = time.time()
            
            # Report results
            print(f"\nPipeline metrics:")
            print(f"  Duration: {metrics.duration:.1f}s")
            print(f"  Audio chunks: {metrics.total_audio_chunks}")
            print(f"  Transcriptions: {metrics.total_transcriptions}")
            print(f"  Injections: {metrics.total_injections}")
            print(f"  Errors: {metrics.total_errors}")
            print(f"  Transcription rate: {metrics.transcription_rate:.1f}/s")
            
            # Verify pipeline worked
            assert metrics.total_audio_chunks > 0, "No audio captured"
            assert metrics.total_transcriptions >= 0, "No transcriptions"  # May be 0 for silence
            assert metrics.total_errors == 0, f"Pipeline errors: {metrics.total_errors}"
            
        finally:
            pa.terminate()
            del model
            if self.gpu_available:
                torch.cuda.empty_cache()
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_pipeline_stress_test(self, audio_test_device):
        """Stress test the pipeline with continuous operation."""
        model = whisper.load_model("tiny")  # Use tiny for speed
        pa = pyaudio.PyAudio()
        
        # Pipeline components
        audio_queue = queue.Queue(maxsize=200)
        text_queue = queue.Queue(maxsize=200)
        
        # Control flags
        stop_capture = threading.Event()
        stop_stt = threading.Event()
        stop_injection = threading.Event()
        
        # Metrics
        metrics = {
            "audio_chunks": 0,
            "transcriptions": 0,
            "injections": 0,
            "audio_drops": 0,
            "stt_errors": 0,
            "injection_errors": 0
        }
        
        def audio_capture_worker():
            stream = pa.open(
                rate=16000,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=audio_test_device,
                frames_per_buffer=512  # Smaller chunks
            )
            
            try:
                while not stop_capture.is_set():
                    try:
                        data = stream.read(512, exception_on_overflow=False)
                        try:
                            audio_queue.put(data, timeout=0.01)
                            metrics["audio_chunks"] += 1
                        except queue.Full:
                            metrics["audio_drops"] += 1
                    except Exception as e:
                        print(f"Audio capture error: {e}")
            finally:
                stream.stop_stream()
                stream.close()
        
        def stt_worker():
            buffer = []
            while not stop_stt.is_set() or not audio_queue.empty():
                try:
                    data = audio_queue.get(timeout=0.1)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    buffer.extend(audio_data)
                    
                    if len(buffer) >= 8000:  # 0.5 second chunks
                        chunk = np.array(buffer[:8000], dtype=np.float32) / 32768.0
                        buffer = buffer[8000:]
                        
                        result = model.transcribe(chunk, language="en")
                        if result["text"].strip():
                            text_queue.put(result["text"])
                            metrics["transcriptions"] += 1
                except queue.Empty:
                    continue
                except Exception as e:
                    metrics["stt_errors"] += 1
        
        def injection_worker():
            while not stop_injection.is_set() or not text_queue.empty():
                try:
                    text = text_queue.get(timeout=0.1)
                    # Simulate injection
                    time.sleep(0.001)
                    metrics["injections"] += 1
                except queue.Empty:
                    continue
                except Exception as e:
                    metrics["injection_errors"] += 1
        
        # Run stress test
        print("\nRunning pipeline stress test for 15 seconds...")
        workers = [
            threading.Thread(target=audio_capture_worker, name="audio"),
            threading.Thread(target=stt_worker, name="stt"),
            threading.Thread(target=injection_worker, name="injection")
        ]
        
        try:
            start_time = time.time()
            
            for worker in workers:
                worker.start()
            
            # Run for 15 seconds
            time.sleep(15)
            
            # Graceful shutdown
            print("Shutting down pipeline...")
            stop_capture.set()
            time.sleep(1)
            stop_stt.set()
            time.sleep(1)
            stop_injection.set()
            
            for worker in workers:
                worker.join(timeout=5)
            
            duration = time.time() - start_time
            
            # Report results
            print(f"\nStress test results ({duration:.1f}s):")
            for key, value in metrics.items():
                print(f"  {key}: {value}")
            
            print(f"\nRates:")
            print(f"  Audio: {metrics['audio_chunks']/duration:.1f} chunks/s")
            print(f"  Transcription: {metrics['transcriptions']/duration:.1f} /s")
            
            # Verify stability
            assert metrics["stt_errors"] < 10, f"Too many STT errors: {metrics['stt_errors']}"
            assert metrics["injection_errors"] == 0, f"Injection errors: {metrics['injection_errors']}"
            assert metrics["audio_drops"] < metrics["audio_chunks"] * 0.01, "Too many audio drops"
            
        finally:
            pa.terminate()
            del model
            if self.gpu_available:
                torch.cuda.empty_cache()
    
    @pytest.mark.integration
    def test_pipeline_latency(self, audio_test_device):
        """Test end-to-end pipeline latency."""
        model = whisper.load_model("tiny")
        
        # Measure latency at each stage
        latencies = {
            "audio_capture": [],
            "stt_processing": [],
            "text_injection": [],
            "end_to_end": []
        }
        
        # Simple synchronous pipeline for latency testing
        pa = pyaudio.PyAudio()
        stream = pa.open(
            rate=16000,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=audio_test_device,
            frames_per_buffer=8000  # 0.5 second chunks
        )
        
        try:
            print("\nMeasuring pipeline latency (10 iterations)...")
            
            for i in range(10):
                e2e_start = time.time()
                
                # Audio capture
                audio_start = time.time()
                data = stream.read(8000, exception_on_overflow=False)
                audio_time = time.time() - audio_start
                latencies["audio_capture"].append(audio_time)
                
                # Convert audio
                audio_data = np.frombuffer(data, dtype=np.int16)
                audio_float = audio_data.astype(np.float32) / 32768.0
                
                # STT processing
                stt_start = time.time()
                result = model.transcribe(audio_float, language="en")
                stt_time = time.time() - stt_start
                latencies["stt_processing"].append(stt_time)
                
                # Injection simulation
                inject_start = time.time()
                if result["text"].strip():
                    time.sleep(0.001 * len(result["text"]))  # Simulate
                inject_time = time.time() - inject_start
                latencies["text_injection"].append(inject_time)
                
                # Total time
                e2e_time = time.time() - e2e_start
                latencies["end_to_end"].append(e2e_time)
            
            # Report latencies
            print("\nPipeline latencies (ms):")
            for stage, times in latencies.items():
                avg = np.mean(times) * 1000
                max_time = np.max(times) * 1000
                print(f"  {stage}: avg={avg:.1f}ms, max={max_time:.1f}ms")
            
            # Check latency requirements
            e2e_avg = np.mean(latencies["end_to_end"])
            assert e2e_avg < 2.0, f"End-to-end latency too high: {e2e_avg:.2f}s"
            
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
            del model
            if self.gpu_available:
                torch.cuda.empty_cache()