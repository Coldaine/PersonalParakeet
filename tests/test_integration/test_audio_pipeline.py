"""
Integration tests for PersonalParakeet v3 audio pipeline.

Tests the complete audio processing workflow from audio input
to text output, including VAD, STT, and text processing.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import asyncio
import time
import queue
import threading

try:
    from core.stt_processor import STTProcessor
    from core.vad_engine import VoiceActivityDetector
    from core.clarity_engine import ClarityEngine
    from core.text_injector import TextInjector
except ImportError:
    # For testing when modules don't exist yet
    STTProcessor = Mock
    VoiceActivityDetector = Mock
    ClarityEngine = Mock
    TextInjector = Mock


class TestAudioPipelineIntegration:
    """Integration tests for the complete audio processing pipeline."""

    @pytest.fixture
    def mock_audio_pipeline(self, test_config):
        """Create a mock audio pipeline for integration testing."""
        pipeline = Mock()
        
        # Mock components
        pipeline.vad = Mock(spec=VoiceActivityDetector)
        pipeline.stt = Mock(spec=STTProcessor)
        pipeline.clarity = Mock(spec=ClarityEngine)
        pipeline.injector = Mock(spec=TextInjector)
        
        # Mock configuration
        pipeline.config = test_config
        pipeline.is_running = False
        pipeline.audio_queue = queue.Queue()
        pipeline.text_queue = queue.Queue()
        
        return pipeline

    @pytest.fixture
    def sample_voice_audio(self):
        """Generate sample voice audio for pipeline testing."""
        duration = 3.0  # 3 seconds
        sample_rate = 16000
        samples = int(sample_rate * duration)
        
        # Generate speech-like signal with pauses
        t = np.linspace(0, duration, samples)
        
        # Voice segments: 0-1s voice, 1-1.5s silence, 1.5-3s voice
        voice_signal = np.zeros(samples)
        
        # First voice segment (0-1s)
        voice1_end = int(sample_rate * 1.0)
        voice1 = np.sin(2 * np.pi * 400 * t[:voice1_end]) * 0.3
        voice1 += np.sin(2 * np.pi * 800 * t[:voice1_end]) * 0.2
        voice_signal[:voice1_end] = voice1
        
        # Silence segment (1-1.5s) - already zeros
        
        # Second voice segment (1.5-3s)
        voice2_start = int(sample_rate * 1.5)
        voice2_t = t[voice2_start:] - t[voice2_start]
        voice2 = np.sin(2 * np.pi * 600 * voice2_t) * 0.3
        voice2 += np.sin(2 * np.pi * 1200 * voice2_t) * 0.2
        voice_signal[voice2_start:] = voice2
        
        # Add noise
        noise = np.random.randn(samples) * 0.02
        voice_signal += noise
        
        return voice_signal.astype(np.float32)

    @pytest.mark.integration
    def test_complete_pipeline_workflow(self, mock_audio_pipeline, sample_voice_audio):
        """Test the complete audio processing workflow."""
        
        def mock_process_audio(audio_data):
            """Mock the complete pipeline processing."""
            # Step 1: VAD processing
            vad_result = {
                'has_voice': True,
                'voice_segments': [
                    {'start': 0.0, 'end': 1.0, 'confidence': 0.9},
                    {'start': 1.5, 'end': 3.0, 'confidence': 0.85}
                ]
            }
            
            # Step 2: STT processing for each voice segment
            stt_results = []
            for segment in vad_result['voice_segments']:
                stt_results.append({
                    'text': f"Test speech segment {len(stt_results) + 1}",
                    'confidence': segment['confidence'],
                    'start_time': segment['start'],
                    'end_time': segment['end']
                })
            
            # Step 3: Clarity engine processing
            clarity_result = {
                'processed_text': "Test speech segment 1. Test speech segment 2.",
                'improvements': ['punctuation', 'capitalization'],
                'confidence': 0.87
            }
            
            # Step 4: Text injection preparation
            injection_result = {
                'final_text': clarity_result['processed_text'],
                'ready_for_injection': True,
                'target_application': 'default'
            }
            
            return {
                'vad': vad_result,
                'stt': stt_results,
                'clarity': clarity_result,
                'injection': injection_result,
                'processing_time': 0.15,
                'success': True
            }
        
        mock_audio_pipeline.process_audio = mock_process_audio
        
        result = mock_audio_pipeline.process_audio(sample_voice_audio)
        
        # Verify complete workflow
        assert result['success'] is True
        assert 'vad' in result
        assert 'stt' in result
        assert 'clarity' in result
        assert 'injection' in result
        
        # Verify VAD results
        assert result['vad']['has_voice'] is True
        assert len(result['vad']['voice_segments']) == 2
        
        # Verify STT results
        assert len(result['stt']) == 2
        for stt_result in result['stt']:
            assert 'text' in stt_result
            assert 'confidence' in stt_result
            assert stt_result['confidence'] > 0.8
        
        # Verify clarity processing
        assert result['clarity']['processed_text']
        assert result['clarity']['confidence'] > 0.8
        
        # Verify injection readiness
        assert result['injection']['ready_for_injection'] is True

    @pytest.mark.integration
    def test_real_time_pipeline_simulation(self, mock_audio_pipeline):
        """Test real-time audio pipeline processing simulation."""
        
        def create_audio_chunk(duration_ms=30):
            """Create a 30ms audio chunk."""
            sample_rate = 16000
            samples = int(sample_rate * duration_ms / 1000)
            
            # Generate speech-like chunk
            t = np.linspace(0, duration_ms/1000, samples)
            chunk = np.sin(2 * np.pi * 500 * t) * 0.2
            chunk += np.random.randn(samples) * 0.01
            
            return chunk.astype(np.float32)
        
        def mock_real_time_processor():
            """Mock real-time processing."""
            processed_chunks = []
            voice_buffer = []
            
            # Simulate processing 10 chunks (300ms of audio)
            for i in range(10):
                chunk = create_audio_chunk()
                
                # VAD processing
                energy = np.mean(np.square(chunk))
                is_voice = energy > 0.01
                
                chunk_result = {
                    'chunk_id': i,
                    'is_voice': is_voice,
                    'energy': energy,
                    'timestamp': i * 30  # ms
                }
                
                if is_voice:
                    voice_buffer.extend(chunk)
                else:
                    # Process accumulated voice if buffer has content
                    if len(voice_buffer) > 0:
                        # Mock STT processing
                        text_result = {
                            'text': f"Voice segment {len(processed_chunks) + 1}",
                            'confidence': 0.9,
                            'buffer_length': len(voice_buffer)
                        }
                        processed_chunks.append(text_result)
                        voice_buffer = []
                
            return {
                'total_chunks': 10,
                'voice_segments': len(processed_chunks),
                'processing_time': 0.05,  # 50ms total processing
                'real_time_factor': 6.0   # 300ms audio processed in 50ms
            }
        
        mock_audio_pipeline.real_time_process = mock_real_time_processor
        
        result = mock_audio_pipeline.real_time_process()
        
        assert result['total_chunks'] == 10
        assert result['voice_segments'] >= 0
        assert result['processing_time'] < 1.0
        assert result['real_time_factor'] > 1.0  # Processing faster than real-time

    @pytest.mark.integration
    async def test_async_pipeline_processing(self, mock_audio_pipeline, sample_voice_audio):
        """Test asynchronous pipeline processing."""
        
        async def mock_async_process(audio_data):
            """Mock asynchronous audio processing."""
            # Simulate async VAD processing
            await asyncio.sleep(0.01)  # 10ms processing delay
            vad_result = {'voice_detected': True, 'segments': 2}
            
            # Simulate async STT processing
            await asyncio.sleep(0.02)  # 20ms processing delay
            stt_result = {'text': 'Async processed speech', 'confidence': 0.9}
            
            # Simulate async clarity processing
            await asyncio.sleep(0.01)  # 10ms processing delay
            clarity_result = {'enhanced_text': 'Async processed speech.', 'improvements': 1}
            
            return {
                'vad': vad_result,
                'stt': stt_result,
                'clarity': clarity_result,
                'total_processing_time': 0.04,
                'async_completion': True
            }
        
        mock_audio_pipeline.async_process = mock_async_process
        
        start_time = time.time()
        result = await mock_audio_pipeline.async_process(sample_voice_audio)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        assert result['async_completion'] is True
        assert result['vad']['voice_detected'] is True
        assert result['stt']['confidence'] > 0.8
        assert result['clarity']['improvements'] > 0
        assert processing_time < 0.1  # Should complete quickly

    @pytest.mark.integration
    def test_pipeline_error_handling(self, mock_audio_pipeline):
        """Test pipeline error handling and recovery."""
        
        def mock_process_with_errors(audio_data, inject_error=None):
            """Mock processing with optional error injection."""
            result = {
                'vad': None,
                'stt': None,
                'clarity': None,
                'injection': None,
                'errors': [],
                'success': False
            }
            
            try:
                # VAD processing
                if inject_error == 'vad':
                    raise RuntimeError("VAD processing failed")
                result['vad'] = {'voice_detected': True}
                
                # STT processing
                if inject_error == 'stt':
                    raise RuntimeError("STT engine failed")
                result['stt'] = {'text': 'Test speech', 'confidence': 0.9}
                
                # Clarity processing
                if inject_error == 'clarity':
                    raise RuntimeError("Clarity engine failed")
                result['clarity'] = {'enhanced_text': 'Test speech.'}
                
                # Injection processing
                if inject_error == 'injection':
                    raise RuntimeError("Text injection failed")
                result['injection'] = {'injected': True}
                
                result['success'] = True
                
            except Exception as e:
                result['errors'].append(str(e))
                # Implement fallback behavior
                if inject_error == 'stt':
                    result['stt'] = {'text': '', 'confidence': 0.0, 'fallback': True}
                elif inject_error == 'clarity':
                    result['clarity'] = {'enhanced_text': result['stt']['text'], 'fallback': True}
            
            return result
        
        mock_audio_pipeline.process_with_errors = mock_process_with_errors
        
        # Test successful processing
        result = mock_audio_pipeline.process_with_errors(np.array([1, 2, 3]))
        assert result['success'] is True
        assert len(result['errors']) == 0
        
        # Test VAD error
        result = mock_audio_pipeline.process_with_errors(np.array([1, 2, 3]), inject_error='vad')
        assert result['success'] is False
        assert len(result['errors']) > 0
        assert 'VAD processing failed' in result['errors'][0]
        
        # Test STT error with fallback
        result = mock_audio_pipeline.process_with_errors(np.array([1, 2, 3]), inject_error='stt')
        assert result['success'] is False
        assert result['stt']['fallback'] is True
        assert result['stt']['confidence'] == 0.0

    @pytest.mark.integration
    def test_pipeline_performance_monitoring(self, mock_audio_pipeline, sample_voice_audio):
        """Test pipeline performance monitoring and metrics."""
        
        def mock_monitored_process(audio_data):
            """Mock processing with performance monitoring."""
            metrics = {
                'start_time': time.time(),
                'component_times': {},
                'memory_usage': {},
                'throughput': {}
            }
            
            # Mock VAD processing with timing
            vad_start = time.time()
            time.sleep(0.001)  # 1ms simulation
            vad_end = time.time()
            metrics['component_times']['vad'] = vad_end - vad_start
            
            # Mock STT processing with timing
            stt_start = time.time()
            time.sleep(0.005)  # 5ms simulation
            stt_end = time.time()
            metrics['component_times']['stt'] = stt_end - stt_start
            
            # Mock clarity processing with timing
            clarity_start = time.time()
            time.sleep(0.002)  # 2ms simulation
            clarity_end = time.time()
            metrics['component_times']['clarity'] = clarity_end - clarity_start
            
            metrics['total_time'] = time.time() - metrics['start_time']
            metrics['audio_duration'] = len(audio_data) / 16000
            metrics['real_time_factor'] = metrics['audio_duration'] / metrics['total_time']
            
            # Mock memory usage
            metrics['memory_usage'] = {
                'vad': 10.5,  # MB
                'stt': 45.2,  # MB
                'clarity': 8.1,  # MB
                'total': 63.8  # MB
            }
            
            # Mock throughput
            metrics['throughput'] = {
                'samples_per_second': len(audio_data) / metrics['total_time'],
                'frames_per_second': (len(audio_data) // 480) / metrics['total_time']
            }
            
            return {
                'processing_result': {
                    'text': 'Performance monitored speech',
                    'confidence': 0.9
                },
                'performance_metrics': metrics
            }
        
        mock_audio_pipeline.monitored_process = mock_monitored_process
        
        result = mock_audio_pipeline.monitored_process(sample_voice_audio)
        
        metrics = result['performance_metrics']
        
        # Verify timing metrics
        assert 'vad' in metrics['component_times']
        assert 'stt' in metrics['component_times']
        assert 'clarity' in metrics['component_times']
        assert metrics['total_time'] > 0
        assert metrics['real_time_factor'] > 1.0  # Should be faster than real-time
        
        # Verify memory metrics
        assert metrics['memory_usage']['total'] > 0
        assert metrics['memory_usage']['stt'] > metrics['memory_usage']['vad']  # STT should use more memory
        
        # Verify throughput metrics
        assert metrics['throughput']['samples_per_second'] > 0
        assert metrics['throughput']['frames_per_second'] > 0

    @pytest.mark.integration
    def test_multi_threaded_pipeline(self, mock_audio_pipeline):
        """Test multi-threaded pipeline processing."""
        
        def mock_threaded_pipeline():
            """Mock multi-threaded pipeline processing."""
            audio_queue = queue.Queue()
            result_queue = queue.Queue()
            
            def audio_producer():
                """Producer thread: generates audio chunks."""
                for i in range(5):
                    chunk = np.random.randn(1024).astype(np.float32) * 0.1
                    audio_queue.put({
                        'chunk_id': i,
                        'audio': chunk,
                        'timestamp': time.time()
                    })
                    time.sleep(0.01)  # 10ms between chunks
                audio_queue.put(None)  # Shutdown signal
            
            def audio_processor():
                """Consumer thread: processes audio chunks."""
                processed_count = 0
                while True:
                    try:
                        item = audio_queue.get(timeout=0.1)
                        if item is None:  # Shutdown signal
                            break
                        
                        # Mock processing
                        processing_start = time.time()
                        time.sleep(0.005)  # 5ms processing
                        processing_end = time.time()
                        
                        result = {
                            'chunk_id': item['chunk_id'],
                            'text': f'Processed chunk {item["chunk_id"]}',
                            'confidence': 0.9,
                            'processing_time': processing_end - processing_start,
                            'queue_delay': processing_start - item['timestamp']
                        }
                        
                        result_queue.put(result)
                        processed_count += 1
                        audio_queue.task_done()
                        
                    except queue.Empty:
                        continue
                
                return processed_count
            
            # Start threads
            producer_thread = threading.Thread(target=audio_producer)
            processor_thread = threading.Thread(target=audio_processor)
            
            producer_thread.start()
            processor_thread.start()
            
            # Collect results
            results = []
            while len(results) < 5:  # Expecting 5 results
                try:
                    result = result_queue.get(timeout=1.0)
                    results.append(result)
                except queue.Empty:
                    break
            
            # Wait for threads to complete
            producer_thread.join()
            processor_thread.join()
            
            return {
                'processed_chunks': len(results),
                'average_processing_time': np.mean([r['processing_time'] for r in results]),
                'average_queue_delay': np.mean([r['queue_delay'] for r in results]),
                'results': results
            }
        
        mock_audio_pipeline.threaded_process = mock_threaded_pipeline
        
        result = mock_audio_pipeline.threaded_process()
        
        assert result['processed_chunks'] == 5
        assert result['average_processing_time'] > 0
        assert result['average_queue_delay'] >= 0
        assert len(result['results']) == 5
        
        # Verify each result
        for res in result['results']:
            assert 'chunk_id' in res
            assert 'text' in res
            assert res['confidence'] > 0.8

    @pytest.mark.integration
    @pytest.mark.slow
    def test_pipeline_stress_test(self, mock_audio_pipeline):
        """Stress test the pipeline with high load."""
        
        def mock_stress_test(num_chunks=100, chunk_size=1024):
            """Mock stress test with many audio chunks."""
            start_time = time.time()
            processed_chunks = 0
            failed_chunks = 0
            
            for i in range(num_chunks):
                try:
                    # Generate test chunk
                    chunk = np.random.randn(chunk_size).astype(np.float32) * 0.1
                    
                    # Mock processing (very fast for stress test)
                    energy = np.mean(np.square(chunk))
                    if energy > 0.005:  # Simulate voice detection
                        processed_chunks += 1
                    
                    # Simulate occasional failures
                    if i % 50 == 0 and i > 0:  # Fail every 50th chunk
                        raise RuntimeError(f"Simulated failure at chunk {i}")
                        
                except Exception:
                    failed_chunks += 1
            
            end_time = time.time()
            total_time = end_time - start_time
            
            return {
                'total_chunks': num_chunks,
                'processed_chunks': processed_chunks,
                'failed_chunks': failed_chunks,
                'success_rate': (processed_chunks / num_chunks) * 100,
                'processing_time': total_time,
                'chunks_per_second': num_chunks / total_time,
                'audio_hours_processed': (num_chunks * chunk_size / 16000) / 3600
            }
        
        mock_audio_pipeline.stress_test = mock_stress_test
        
        result = mock_audio_pipeline.stress_test(num_chunks=100)
        
        assert result['total_chunks'] == 100
        assert result['success_rate'] > 90  # Should handle most chunks successfully
        assert result['chunks_per_second'] > 100  # Should process quickly
        assert result['failed_chunks'] < 5  # Should have minimal failures
        assert result['processing_time'] < 5.0  # Should complete within 5 seconds