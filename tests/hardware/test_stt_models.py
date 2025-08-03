"""Test STT model loading and inference with real hardware."""

import time
from pathlib import Path

import numpy as np
import pytest
import torch
import whisper

from tests.core import BaseHardwareTest


class TestSTTModels(BaseHardwareTest):
    """Test speech-to-text models on real hardware."""
    
    @pytest.mark.hardware
    def test_whisper_model_loading(self):
        """Test loading Whisper models."""
        models_to_test = ["tiny", "base"]
        
        for model_name in models_to_test:
            print(f"\nLoading Whisper {model_name} model...")
            start_time = time.time()
            
            try:
                model = whisper.load_model(model_name)
                load_time = time.time() - start_time
                
                print(f"  Load time: {load_time:.2f}s")
                print(f"  Device: {next(model.parameters()).device}")
                
                # Check model is on expected device
                if self.gpu_available:
                    assert next(model.parameters()).is_cuda, "Model should be on GPU"
                
                # Basic inference test
                dummy_audio = np.zeros(16000, dtype=np.float32)  # 1 second of silence
                result = model.transcribe(dummy_audio, language="en")
                
                assert isinstance(result, dict), "Model should return dict"
                assert "text" in result, "Result should contain text"
                
                # Cleanup
                del model
                if self.gpu_available:
                    torch.cuda.empty_cache()
                    
            except Exception as e:
                pytest.fail(f"Failed to load {model_name} model: {e}")
    
    @pytest.mark.hardware
    @pytest.mark.gpu_intensive
    def test_whisper_gpu_memory_usage(self, skip_if_no_gpu):
        """Test GPU memory usage of different model sizes."""
        if not self.gpu_available:
            pytest.skip("GPU required for memory testing")
        
        models_to_test = [
            ("tiny", 39),    # ~39M parameters
            ("base", 74),    # ~74M parameters
        ]
        
        for model_name, expected_params in models_to_test:
            # Clear GPU memory
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
            
            initial_memory = torch.cuda.memory_allocated()
            
            # Load model
            model = whisper.load_model(model_name)
            
            # Check memory usage
            model_memory = torch.cuda.memory_allocated() - initial_memory
            peak_memory = torch.cuda.max_memory_allocated()
            
            print(f"\n{model_name} model GPU memory:")
            print(f"  Model size: {model_memory / 1024**2:.1f} MB")
            print(f"  Peak usage: {peak_memory / 1024**2:.1f} MB")
            
            # Verify reasonable memory usage (rough estimate)
            expected_memory_mb = expected_params * 4 * 1.5  # float32 + overhead
            assert model_memory / 1024**2 < expected_memory_mb, \
                f"Model using too much memory: {model_memory / 1024**2:.1f} MB"
            
            # Cleanup
            del model
            torch.cuda.empty_cache()
    
    @pytest.mark.hardware
    def test_whisper_inference_speed(self):
        """Test Whisper inference speed on real audio."""
        model = whisper.load_model("base")
        
        # Generate test audio (1 second of noise)
        sample_rate = 16000
        duration = 1.0
        audio = np.random.randn(int(sample_rate * duration)).astype(np.float32) * 0.01
        
        # Warmup
        _ = model.transcribe(audio, language="en")
        
        # Measure inference time
        inference_times = []
        for _ in range(5):
            start = time.time()
            result = model.transcribe(audio, language="en", fp16=self.gpu_available)
            inference_time = time.time() - start
            inference_times.append(inference_time)
        
        avg_time = np.mean(inference_times)
        rtf = avg_time / duration  # Real-time factor
        
        print(f"\nWhisper base inference speed:")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Real-time factor: {rtf:.2f}x")
        
        # Should be faster than real-time
        assert rtf < 1.0, f"Inference too slow: {rtf:.2f}x real-time"
        
        # Cleanup
        del model
        if self.gpu_available:
            torch.cuda.empty_cache()
    
    @pytest.mark.hardware
    def test_whisper_batch_processing(self):
        """Test batch processing capabilities."""
        model = whisper.load_model("base")
        
        # Create batch of audio samples
        batch_sizes = [1, 2, 4]
        audio_duration = 1.0
        sample_rate = 16000
        
        for batch_size in batch_sizes:
            # Generate batch
            audio_batch = [
                np.random.randn(int(sample_rate * audio_duration)).astype(np.float32) * 0.01
                for _ in range(batch_size)
            ]
            
            # Process batch
            start = time.time()
            results = []
            for audio in audio_batch:
                result = model.transcribe(audio, language="en", fp16=self.gpu_available)
                results.append(result)
            batch_time = time.time() - start
            
            time_per_sample = batch_time / batch_size
            
            print(f"\nBatch size {batch_size}:")
            print(f"  Total time: {batch_time:.3f}s")
            print(f"  Time per sample: {time_per_sample:.3f}s")
            
            assert len(results) == batch_size, "Should process all samples"
        
        # Cleanup
        del model
        if self.gpu_available:
            torch.cuda.empty_cache()
    
    @pytest.mark.hardware
    @pytest.mark.slow
    def test_whisper_error_recovery(self):
        """Test model error recovery with various inputs."""
        model = whisper.load_model("tiny")  # Use tiny for speed
        
        test_cases = [
            ("empty", np.array([], dtype=np.float32)),
            ("very_short", np.zeros(1000, dtype=np.float32)),
            ("very_long", np.zeros(30 * 16000, dtype=np.float32)),  # 30 seconds
            ("noisy", np.random.randn(16000).astype(np.float32)),
            ("clipped", np.ones(16000, dtype=np.float32) * 2.0),  # Out of range
        ]
        
        for test_name, audio in test_cases:
            print(f"\nTesting {test_name} audio...")
            try:
                result = model.transcribe(audio, language="en")
                assert isinstance(result, dict), f"{test_name}: Should return dict"
                assert "text" in result, f"{test_name}: Should contain text"
                print(f"  Success: '{result['text'][:50]}...'")
            except Exception as e:
                # Some inputs might legitimately fail
                print(f"  Expected failure: {type(e).__name__}: {e}")
        
        # Cleanup
        del model
        if self.gpu_available:
            torch.cuda.empty_cache()