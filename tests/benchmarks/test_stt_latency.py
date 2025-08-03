"""Benchmark STT latency and throughput."""

import time
from typing import Dict, List

import numpy as np
import pytest
import torch
import whisper

from tests.core import BaseHardwareTest


class TestSTTLatency(BaseHardwareTest):
    """Benchmark speech-to-text latency."""
    
    @pytest.mark.benchmark
    def test_whisper_model_latencies(self):
        """Benchmark latency for different Whisper model sizes."""
        models_to_test = ["tiny", "base"]
        audio_durations = [1.0, 3.0, 5.0]  # seconds
        
        results = {}
        
        for model_name in models_to_test:
            print(f"\nBenchmarking {model_name} model...")
            model = whisper.load_model(model_name)
            model_results = {}
            
            for duration in audio_durations:
                # Generate test audio
                sample_rate = 16000
                samples = int(sample_rate * duration)
                audio = np.random.randn(samples).astype(np.float32) * 0.01
                
                # Warmup
                _ = model.transcribe(audio, language="en")
                
                # Benchmark
                latencies = []
                for _ in range(10):
                    start = time.time()
                    _ = model.transcribe(audio, language="en", fp16=self.gpu_available)
                    latency = time.time() - start
                    latencies.append(latency)
                
                avg_latency = np.mean(latencies)
                std_latency = np.std(latencies)
                rtf = avg_latency / duration
                
                model_results[duration] = {
                    "avg_latency": avg_latency,
                    "std_latency": std_latency,
                    "rtf": rtf,
                    "throughput": 1.0 / avg_latency
                }
            
            results[model_name] = model_results
            del model
            if self.gpu_available:
                torch.cuda.empty_cache()
        
        # Print results table
        print("\n" + "="*70)
        print("STT Latency Benchmark Results")
        print("="*70)
        print(f"{'Model':<10} {'Duration':<10} {'Latency':<15} {'RTF':<10} {'Throughput':<10}")
        print("-"*70)
        
        for model_name, model_results in results.items():
            for duration, metrics in model_results.items():
                print(f"{model_name:<10} {duration:<10.1f} "
                      f"{metrics['avg_latency']*1000:<15.1f} "
                      f"{metrics['rtf']:<10.3f} "
                      f"{metrics['throughput']:<10.1f}")
        
        # Verify performance
        for model_name, model_results in results.items():
            for duration, metrics in model_results.items():
                assert metrics['rtf'] < 1.0, \
                    f"{model_name} not real-time for {duration}s audio: RTF={metrics['rtf']:.3f}"
    
    @pytest.mark.benchmark
    @pytest.mark.gpu_intensive
    def test_batch_processing_performance(self, skip_if_no_gpu):
        """Benchmark batch vs sequential processing."""
        model = whisper.load_model("base")
        
        batch_sizes = [1, 2, 4, 8]
        audio_duration = 2.0
        sample_rate = 16000
        
        results = {}
        
        for batch_size in batch_sizes:
            # Generate batch of audio
            audios = [
                np.random.randn(int(sample_rate * audio_duration)).astype(np.float32) * 0.01
                for _ in range(batch_size)
            ]
            
            # Sequential processing
            seq_start = time.time()
            for audio in audios:
                _ = model.transcribe(audio, language="en", fp16=True)
            seq_time = time.time() - seq_start
            
            # Batch processing simulation (still sequential but minimal overhead)
            batch_start = time.time()
            for audio in audios:
                _ = model.transcribe(audio, language="en", fp16=True, verbose=False)
            batch_time = time.time() - batch_start
            
            results[batch_size] = {
                "sequential_time": seq_time,
                "batch_time": batch_time,
                "speedup": seq_time / batch_time,
                "per_sample_time": batch_time / batch_size
            }
        
        print("\n" + "="*60)
        print("Batch Processing Performance")
        print("="*60)
        print(f"{'Batch Size':<12} {'Seq Time':<12} {'Batch Time':<12} {'Per Sample':<12}")
        print("-"*60)
        
        for batch_size, metrics in results.items():
            print(f"{batch_size:<12} "
                  f"{metrics['sequential_time']:<12.3f} "
                  f"{metrics['batch_time']:<12.3f} "
                  f"{metrics['per_sample_time']:<12.3f}")
        
        del model
        if self.gpu_available:
            torch.cuda.empty_cache()
    
    @pytest.mark.benchmark
    def test_audio_length_scaling(self):
        """Test how latency scales with audio length."""
        model = whisper.load_model("tiny")
        
        durations = [0.5, 1.0, 2.0, 5.0, 10.0]
        sample_rate = 16000
        
        results = []
        
        for duration in durations:
            # Generate audio
            samples = int(sample_rate * duration)
            audio = np.random.randn(samples).astype(np.float32) * 0.01
            
            # Measure latency
            latencies = []
            for _ in range(5):
                start = time.time()
                _ = model.transcribe(audio, language="en")
                latency = time.time() - start
                latencies.append(latency)
            
            avg_latency = np.mean(latencies)
            
            results.append({
                "duration": duration,
                "latency": avg_latency,
                "rtf": avg_latency / duration,
                "latency_per_second": avg_latency / duration
            })
        
        print("\n" + "="*60)
        print("Audio Length Scaling")
        print("="*60)
        print(f"{'Duration (s)':<12} {'Latency (ms)':<15} {'RTF':<10} {'ms/s':<10}")
        print("-"*60)
        
        for r in results:
            print(f"{r['duration']:<12.1f} "
                  f"{r['latency']*1000:<15.1f} "
                  f"{r['rtf']:<10.3f} "
                  f"{r['latency_per_second']*1000:<10.1f}")
        
        # Check scaling is reasonable (should be sub-linear)
        short_rtf = results[0]['rtf']  # 0.5s audio
        long_rtf = results[-1]['rtf']   # 10s audio
        
        assert long_rtf < short_rtf * 2, \
            f"Poor scaling: RTF increased from {short_rtf:.3f} to {long_rtf:.3f}"
        
        del model
        if self.gpu_available:
            torch.cuda.empty_cache()
    
    @pytest.mark.benchmark
    @pytest.mark.slow
    def test_sustained_throughput(self):
        """Test sustained STT throughput over time."""
        model = whisper.load_model("tiny")
        
        test_duration = 30  # seconds
        audio_chunk_duration = 1.0
        sample_rate = 16000
        
        # Generate audio chunk
        samples = int(sample_rate * audio_chunk_duration)
        audio = np.random.randn(samples).astype(np.float32) * 0.01
        
        print(f"\nRunning sustained throughput test for {test_duration}s...")
        
        start_time = time.time()
        transcriptions = 0
        latencies = []
        
        while time.time() - start_time < test_duration:
            chunk_start = time.time()
            _ = model.transcribe(audio, language="en")
            chunk_latency = time.time() - chunk_start
            
            transcriptions += 1
            latencies.append(chunk_latency)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        avg_latency = np.mean(latencies)
        p50_latency = np.percentile(latencies, 50)
        p95_latency = np.percentile(latencies, 95)
        p99_latency = np.percentile(latencies, 99)
        throughput = transcriptions / total_time
        
        print(f"\nSustained Throughput Results:")
        print(f"  Total transcriptions: {transcriptions}")
        print(f"  Total time: {total_time:.1f}s")
        print(f"  Throughput: {throughput:.1f} transcriptions/s")
        print(f"\nLatency Statistics (ms):")
        print(f"  Average: {avg_latency*1000:.1f}")
        print(f"  P50: {p50_latency*1000:.1f}")
        print(f"  P95: {p95_latency*1000:.1f}")
        print(f"  P99: {p99_latency*1000:.1f}")
        
        # Verify sustained performance
        assert throughput > 0.9 / audio_chunk_duration, \
            f"Throughput too low: {throughput:.1f} transcriptions/s"
        assert p99_latency < audio_chunk_duration * 2, \
            f"P99 latency too high: {p99_latency:.3f}s"
        
        del model
        if self.gpu_available:
            torch.cuda.empty_cache()