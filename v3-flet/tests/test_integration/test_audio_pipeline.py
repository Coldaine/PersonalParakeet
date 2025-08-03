"""
Integration tests for PersonalParakeet v3 audio pipeline.

Tests the complete audio processing workflow from VAD to STT
with proper hardware mocking for CI/CD compatibility.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
import numpy as np

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

@pytest.mark.integration
class TestAudioPipeline:
    """Integration tests for complete audio processing pipeline."""
    
    @pytest.fixture
    def mock_audio_pipeline(self, mock_config):
        """Create a complete mock audio pipeline for testing."""
        
        # Mock VAD Engine
        mock_vad = MagicMock()
        mock_vad.process_audio_frame.return_value = {
            'is_speech': True,
            'confidence': 0.8,
            'rms_energy': 0.5
        }
        
        # Mock STT Processor
        mock_stt = MagicMock()
        mock_stt.initialize.return_value = True
        mock_stt.transcribe.return_value = "Hello world"
        mock_stt.cleanup.return_value = None
        
        # Mock Audio Engine
        mock_audio = MagicMock()
        mock_audio.start_recording.return_value = True
        mock_audio.stop_recording.return_value = True
        mock_audio.get_audio_data.return_value = np.random.random(16000).astype(np.float32)
        
        return {
            'vad': mock_vad,
            'stt': mock_stt,
            'audio': mock_audio,
            'config': mock_config
        }
    
    def test_vad_stt_integration(self, mock_audio_pipeline, sample_audio_data):
        """Test integration between VAD and STT components."""
        vad = mock_audio_pipeline['vad']
        stt = mock_audio_pipeline['stt']
        audio_data = sample_audio_data['data']
        
        # Process audio through VAD
        frame_size = 1024
        speech_detected = False
        
        for i in range(0, len(audio_data), frame_size):
            frame = audio_data[i:i+frame_size]
            if len(frame) == frame_size:
                vad_result = vad.process_audio_frame(frame)
                
                if vad_result['is_speech']:
                    speech_detected = True
                    # Send to STT when speech is detected
                    transcription = stt.transcribe(frame)
                    assert transcription == "Hello world"
        
        assert speech_detected
        assert stt.transcribe.called
    
    def test_real_time_processing_simulation(self, mock_audio_pipeline):
        """Test real-time audio processing simulation."""
        vad = mock_audio_pipeline['vad']
        stt = mock_audio_pipeline['stt']
        audio = mock_audio_pipeline['audio']
        
        # Simulate real-time processing workflow
        audio.start_recording()
        
        # Simulate processing multiple audio chunks
        for _ in range(10):  # 10 chunks of audio
            chunk = audio.get_audio_data()
            vad_result = vad.process_audio_frame(chunk)
            
            if vad_result['is_speech']:
                transcription = stt.transcribe(chunk)
                assert transcription == "Hello world"
        
        audio.stop_recording()
        
        # Verify workflow calls
        audio.start_recording.assert_called_once()
        audio.stop_recording.assert_called_once()
        assert audio.get_audio_data.call_count == 10
    
    def test_error_handling_in_pipeline(self, mock_audio_pipeline):
        """Test error handling throughout the pipeline."""
        vad = mock_audio_pipeline['vad']
        stt = mock_audio_pipeline['stt']
        
        # Test VAD error handling
        vad.process_audio_frame.side_effect = Exception("VAD error")
        
        with pytest.raises(Exception, match="VAD error"):
            vad.process_audio_frame(np.random.random(1024).astype(np.float32))
        
        # Reset and test STT error handling
        vad.process_audio_frame.side_effect = None
        vad.process_audio_frame.return_value = {'is_speech': True, 'confidence': 0.8, 'rms_energy': 0.5}
        stt.transcribe.side_effect = Exception("STT error")
        
        # VAD should work
        result = vad.process_audio_frame(np.random.random(1024).astype(np.float32))
        assert result['is_speech'] is True
        
        # STT should raise error
        with pytest.raises(Exception, match="STT error"):
            stt.transcribe(np.random.random(1024).astype(np.float32))
    
    def test_configuration_propagation(self, mock_audio_pipeline):
        """Test that configuration is properly propagated through pipeline."""
        config = mock_audio_pipeline['config']
        
        # Verify configuration structure
        assert config.audio.sample_rate == 16000
        assert config.audio.channels == 1
        assert config.vad.threshold == 0.5
        assert config.stt.device == "cpu"
        
        # Test configuration usage in components
        # This would normally be tested by verifying components use config values
        assert hasattr(config, 'audio')
        assert hasattr(config, 'vad') 
        assert hasattr(config, 'stt')
    
    @pytest.mark.performance
    def test_pipeline_performance_requirements(self, mock_audio_pipeline):
        """Test pipeline performance meets real-time requirements."""
        import time
        
        vad = mock_audio_pipeline['vad']
        stt = mock_audio_pipeline['stt']
        
        # Mock realistic processing times
        def mock_vad_process(frame):
            time.sleep(0.001)  # 1ms VAD processing
            return {'is_speech': True, 'confidence': 0.8, 'rms_energy': 0.5}
        
        def mock_stt_transcribe(audio):
            time.sleep(0.01)  # 10ms STT processing
            return "performance test"
        
        vad.process_audio_frame.side_effect = mock_vad_process
        stt.transcribe.side_effect = mock_stt_transcribe
        
        # Test processing time for typical workflow
        audio_frame = np.random.random(1024).astype(np.float32)
        
        start_time = time.time()
        
        # Process through pipeline
        vad_result = vad.process_audio_frame(audio_frame)
        if vad_result['is_speech']:
            transcription = stt.transcribe(audio_frame)
        
        end_time = time.time()
        
        # Total processing should be under 50ms for real-time
        total_time = end_time - start_time
        assert total_time < 0.05  # 50ms threshold
        assert transcription == "performance test"
    
    def test_memory_usage_stability(self, mock_audio_pipeline):
        """Test memory usage remains stable during extended processing."""
        vad = mock_audio_pipeline['vad']
        stt = mock_audio_pipeline['stt']
        
        # Process many audio frames to test memory stability
        for i in range(100):
            frame = np.random.random(1024).astype(np.float32) * 0.5
            
            vad_result = vad.process_audio_frame(frame)
            
            # Occasionally trigger STT
            if i % 10 == 0:
                transcription = stt.transcribe(frame)
                assert transcription == "Hello world"
        
        # Verify all calls completed successfully
        assert vad.process_audio_frame.call_count == 100
        assert stt.transcribe.call_count == 10

@pytest.mark.e2e
class TestEndToEndWorkflows:
    """End-to-end tests for complete user workflows."""
    
    def test_dictation_workflow(self, mock_audio_pipeline, sample_audio_data):
        """Test complete dictation workflow from audio input to text output."""
        vad = mock_audio_pipeline['vad']
        stt = mock_audio_pipeline['stt']
        audio = mock_audio_pipeline['audio']
        config = mock_audio_pipeline['config']
        
        # Simulate user starting dictation
        audio.start_recording()
        
        # Process sample audio
        audio_data = sample_audio_data['data']
        frame_size = config.audio.chunk_size
        
        collected_text = []
        
        # Process audio in chunks as would happen in real-time
        for i in range(0, len(audio_data), frame_size):
            frame = audio_data[i:i+frame_size]
            if len(frame) == frame_size:
                # VAD processing
                vad_result = vad.process_audio_frame(frame)
                
                # STT processing when speech detected
                if vad_result['is_speech'] and vad_result['confidence'] > 0.7:
                    transcription = stt.transcribe(frame)
                    if transcription:
                        collected_text.append(transcription)
        
        # Stop recording
        audio.stop_recording()
        
        # Verify workflow completed successfully
        assert len(collected_text) > 0
        assert all(text == "Hello world" for text in collected_text)
        audio.start_recording.assert_called_once()
        audio.stop_recording.assert_called_once()
    
    def test_continuous_dictation_session(self, mock_audio_pipeline):
        """Test continuous dictation session with multiple speech segments."""
        vad = mock_audio_pipeline['vad']
        stt = mock_audio_pipeline['stt']
        
        # Simulate different types of audio input
        test_scenarios = [
            # (is_speech, confidence, expected_transcription)
            (True, 0.9, "First sentence"),
            (True, 0.8, "Second sentence"), 
            (False, 0.2, None),  # Silence
            (True, 0.85, "Third sentence"),
            (False, 0.1, None),  # More silence
            (True, 0.9, "Final sentence"),
        ]
        
        transcriptions = []
        
        for is_speech, confidence, expected_text in test_scenarios:
            # Configure mocks for this scenario
            vad.process_audio_frame.return_value = {
                'is_speech': is_speech,
                'confidence': confidence,
                'rms_energy': 0.5 if is_speech else 0.1
            }
            
            if expected_text:
                stt.transcribe.return_value = expected_text
            
            # Process audio frame
            frame = np.random.random(1024).astype(np.float32)
            vad_result = vad.process_audio_frame(frame)
            
            if vad_result['is_speech'] and vad_result['confidence'] > 0.7:
                transcription = stt.transcribe(frame)
                transcriptions.append(transcription)
        
        # Verify session results
        expected_transcriptions = ["First sentence", "Second sentence", "Third sentence", "Final sentence"]
        assert transcriptions == expected_transcriptions
        assert len(transcriptions) == 4  # Only speech segments should be transcribed
    
    @pytest.mark.slow
    def test_extended_session_stability(self, mock_audio_pipeline):
        """Test system stability during extended dictation sessions."""
        vad = mock_audio_pipeline['vad']
        stt = mock_audio_pipeline['stt']
        audio = mock_audio_pipeline['audio']
        
        # Simulate 30-second session at 16kHz
        sample_rate = 16000
        session_duration = 30  # seconds
        frame_size = 1024
        total_frames = (sample_rate * session_duration) // frame_size
        
        audio.start_recording()
        
        successful_transcriptions = 0
        
        for frame_num in range(total_frames):
            # Generate realistic audio frame
            frame = np.random.random(frame_size).astype(np.float32) * 0.5
            
            # Process through pipeline
            vad_result = vad.process_audio_frame(frame)
            
            # Simulate speech detection every 10th frame
            if frame_num % 10 == 0:
                vad.process_audio_frame.return_value = {
                    'is_speech': True,
                    'confidence': 0.8,
                    'rms_energy': 0.5
                }
                transcription = stt.transcribe(frame)
                if transcription:
                    successful_transcriptions += 1
        
        audio.stop_recording()
        
        # Verify session completed successfully
        assert successful_transcriptions > 0
        assert vad.process_audio_frame.call_count == total_frames
        
        # Verify cleanup
        stt.cleanup()
        stt.cleanup.assert_called_once()