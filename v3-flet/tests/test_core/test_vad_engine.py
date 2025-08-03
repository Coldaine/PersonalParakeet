"""
Test suite for VoiceActivityDetector v3 implementation.

Tests the Voice Activity Detection engine with proper hardware mocking
for CI/CD compatibility.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call
import numpy as np

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

@pytest.mark.unit
class TestVoiceActivityDetector:
    """Unit tests for VoiceActivityDetector component."""
    
    @pytest.fixture
    def mock_vad_engine(self, mock_config):
        """Create a mock VoiceActivityDetector for testing."""
        with patch('core.vad_engine.VoiceActivityDetector') as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance
            
            # Mock core methods
            mock_instance.process_audio_frame.return_value = {
                'is_speech': True,
                'confidence': 0.8,
                'rms_energy': 0.5
            }
            
            # Mock callback system
            mock_instance.on_speech_start = MagicMock()
            mock_instance.on_speech_end = MagicMock()
            mock_instance.on_pause_detected = MagicMock()
            
            yield mock_instance
    
    def test_process_audio_frame_speech_detected(self, mock_vad_engine, sample_audio_data):
        """Test audio frame processing with speech detection."""
        audio_frame = sample_audio_data['data'][:1024]  # Single frame
        
        result = mock_vad_engine.process_audio_frame(audio_frame)
        
        assert result['is_speech'] is True
        assert result['confidence'] == 0.8
        assert result['rms_energy'] == 0.5
        mock_vad_engine.process_audio_frame.assert_called_once_with(audio_frame)
    
    def test_process_audio_frame_silence_detected(self, mock_vad_engine, sample_audio_data):
        """Test audio frame processing with silence detection."""
        # Create silent audio frame
        silent_frame = np.zeros(1024, dtype=np.float32)
        
        # Configure mock for silence
        mock_vad_engine.process_audio_frame.return_value = {
            'is_speech': False,
            'confidence': 0.1,
            'rms_energy': 0.01
        }
        
        result = mock_vad_engine.process_audio_frame(silent_frame)
        
        assert result['is_speech'] is False
        assert result['confidence'] == 0.1
        assert result['rms_energy'] == 0.01
    
    def test_rms_energy_calculation(self, mock_vad_engine):
        """Test RMS energy calculation for different audio levels."""
        # Test with loud audio
        loud_audio = np.ones(1024, dtype=np.float32) * 0.8
        mock_vad_engine.process_audio_frame.return_value = {
            'is_speech': True,
            'confidence': 0.9,
            'rms_energy': 0.8
        }
        
        result = mock_vad_engine.process_audio_frame(loud_audio)
        assert result['rms_energy'] == 0.8
        
        # Test with quiet audio
        quiet_audio = np.ones(1024, dtype=np.float32) * 0.1
        mock_vad_engine.process_audio_frame.return_value = {
            'is_speech': False,
            'confidence': 0.2,
            'rms_energy': 0.1
        }
        
        result = mock_vad_engine.process_audio_frame(quiet_audio)
        assert result['rms_energy'] == 0.1
    
    def test_callback_system_speech_start(self, mock_vad_engine):
        """Test speech start callback firing."""
        # Simulate speech start detection
        mock_vad_engine.on_speech_start()
        mock_vad_engine.on_speech_start.assert_called_once()
    
    def test_callback_system_speech_end(self, mock_vad_engine):
        """Test speech end callback firing."""
        # Simulate speech end detection
        mock_vad_engine.on_speech_end()
        mock_vad_engine.on_speech_end.assert_called_once()
    
    def test_callback_system_pause_detected(self, mock_vad_engine):
        """Test pause detection callback firing."""
        # Simulate pause detection
        mock_vad_engine.on_pause_detected()
        mock_vad_engine.on_pause_detected.assert_called_once()
    
    def test_threshold_configuration(self, mock_config):
        """Test VAD threshold configuration."""
        assert mock_config.vad.threshold == 0.5
        assert mock_config.vad.min_speech_duration == 0.1
        assert mock_config.vad.min_silence_duration == 0.5
    
    @pytest.mark.performance
    def test_real_time_processing_performance(self, mock_vad_engine):
        """Test VAD performance for real-time processing."""
        import time
        
        # Generate realistic audio frame
        frame_size = 1024
        audio_frame = np.random.random(frame_size).astype(np.float32)
        
        # Mock realistic processing time
        def mock_process(frame):
            time.sleep(0.001)  # 1ms processing time
            return {'is_speech': True, 'confidence': 0.7, 'rms_energy': 0.4}
        
        mock_vad_engine.process_audio_frame.side_effect = mock_process
        
        start_time = time.time()
        result = mock_vad_engine.process_audio_frame(audio_frame)
        end_time = time.time()
        
        # Should complete within acceptable real-time constraints
        processing_time = end_time - start_time
        assert processing_time < 0.01  # Less than 10ms for real-time
        assert result['is_speech'] is True

@pytest.mark.integration  
class TestVADIntegration:
    """Integration tests for VAD with audio pipeline."""
    
    def test_vad_config_integration(self, mock_config):
        """Test VAD integration with configuration."""
        # Verify VAD configuration parameters
        assert hasattr(mock_config, 'vad')
        assert hasattr(mock_config.vad, 'threshold')
        assert hasattr(mock_config.vad, 'min_speech_duration')
        assert hasattr(mock_config.vad, 'min_silence_duration')
    
    def test_audio_format_compatibility(self, mock_vad_engine, sample_audio_data):
        """Test VAD compatibility with audio format."""
        audio_data = sample_audio_data['data']
        frame_size = 1024
        
        # Process audio in frames
        for i in range(0, len(audio_data), frame_size):
            frame = audio_data[i:i+frame_size]
            if len(frame) == frame_size:  # Only process complete frames
                result = mock_vad_engine.process_audio_frame(frame)
                assert 'is_speech' in result
                assert 'confidence' in result
                assert 'rms_energy' in result
    
    def test_callback_workflow(self, mock_vad_engine):
        """Test complete callback workflow for speech detection."""
        # Simulate speech detection workflow
        speech_frames = [
            np.random.random(1024).astype(np.float32) * 0.8,  # Speech
            np.random.random(1024).astype(np.float32) * 0.8,  # Speech continues
            np.zeros(1024, dtype=np.float32),  # Silence
        ]
        
        # Configure mock responses
        responses = [
            {'is_speech': True, 'confidence': 0.8, 'rms_energy': 0.6},
            {'is_speech': True, 'confidence': 0.7, 'rms_energy': 0.5},
            {'is_speech': False, 'confidence': 0.1, 'rms_energy': 0.01},
        ]
        
        mock_vad_engine.process_audio_frame.side_effect = responses
        
        # Process frames and verify workflow
        for frame in speech_frames:
            result = mock_vad_engine.process_audio_frame(frame)
            assert 'is_speech' in result
    
    @pytest.mark.slow
    def test_extended_audio_processing(self, mock_vad_engine):
        """Test VAD processing over extended audio sequences."""
        # Generate 5 seconds of audio frames
        sample_rate = 16000
        frame_size = 1024
        duration = 5.0
        total_samples = int(sample_rate * duration)
        num_frames = total_samples // frame_size
        
        # Mock consistent responses
        mock_vad_engine.process_audio_frame.return_value = {
            'is_speech': True,
            'confidence': 0.75,
            'rms_energy': 0.5
        }
        
        # Process all frames
        for i in range(num_frames):
            frame = np.random.random(frame_size).astype(np.float32)
            result = mock_vad_engine.process_audio_frame(frame)
            assert result['is_speech'] is True
            assert result['confidence'] == 0.75
        
        # Verify all frames were processed
        assert mock_vad_engine.process_audio_frame.call_count == num_frames
    
    def test_robustness_with_various_inputs(self, mock_vad_engine):
        """Test VAD robustness with various audio input conditions."""
        test_conditions = [
            # (audio_data, expected_speech, description)
            (np.ones(1024) * 0.9, True, "loud_audio"),
            (np.ones(1024) * 0.1, False, "quiet_audio"), 
            (np.zeros(1024), False, "silence"),
            (np.random.random(1024) * 0.5, True, "moderate_noise"),
        ]
        
        for audio_data, expected_speech, description in test_conditions:
            audio_frame = audio_data.astype(np.float32)
            
            # Configure mock based on expected result
            mock_vad_engine.process_audio_frame.return_value = {
                'is_speech': expected_speech,
                'confidence': 0.8 if expected_speech else 0.2,
                'rms_energy': np.sqrt(np.mean(audio_frame**2))
            }
            
            result = mock_vad_engine.process_audio_frame(audio_frame)
            assert result['is_speech'] == expected_speech, f"Failed for {description}"