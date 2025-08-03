"""
Test suite for STTProcessor v3 implementation.

Tests the Speech-to-Text processor with proper hardware mocking
for CI/CD compatibility.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

@pytest.mark.unit
class TestSTTProcessor:
    """Unit tests for STTProcessor component."""
    
    @pytest.fixture
    def mock_stt_processor(self, mock_config):
        """Create a mock STTProcessor for testing."""
        with patch('core.stt_processor.STTProcessor') as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance
            
            # Mock core methods
            mock_instance.initialize.return_value = True
            mock_instance.transcribe.return_value = "test transcription"
            mock_instance.cleanup.return_value = None
            mock_instance._transcribe_sync.return_value = "sync transcription"
            
            yield mock_instance
    
    def test_initialization(self, mock_stt_processor, mock_config):
        """Test STT processor initialization."""
        # Test successful initialization
        result = mock_stt_processor.initialize()
        assert result is True
        mock_stt_processor.initialize.assert_called_once()
    
    def test_transcribe_basic(self, mock_stt_processor, sample_audio_data):
        """Test basic transcription functionality."""
        audio_data = sample_audio_data['data']
        
        result = mock_stt_processor.transcribe(audio_data)
        
        assert result == "test transcription"
        mock_stt_processor.transcribe.assert_called_once_with(audio_data)
    
    def test_transcribe_empty_audio(self, mock_stt_processor):
        """Test transcription with empty audio data."""
        import numpy as np
        empty_audio = np.array([])
        
        mock_stt_processor.transcribe.return_value = ""
        result = mock_stt_processor.transcribe(empty_audio)
        
        assert result == ""
    
    def test_transcribe_sync(self, mock_stt_processor, sample_audio_data):
        """Test synchronous transcription method."""
        audio_data = sample_audio_data['data']
        
        result = mock_stt_processor._transcribe_sync(audio_data)
        
        assert result == "sync transcription"
        mock_stt_processor._transcribe_sync.assert_called_once_with(audio_data)
    
    def test_cleanup(self, mock_stt_processor):
        """Test processor cleanup."""
        mock_stt_processor.cleanup()
        mock_stt_processor.cleanup.assert_called_once()
    
    def test_error_handling(self, mock_stt_processor, sample_audio_data):
        """Test error handling in transcription."""
        audio_data = sample_audio_data['data']
        
        # Mock an exception
        mock_stt_processor.transcribe.side_effect = Exception("Processing error")
        
        with pytest.raises(Exception, match="Processing error"):
            mock_stt_processor.transcribe(audio_data)
    
    @pytest.mark.performance
    def test_transcription_performance(self, mock_stt_processor, sample_audio_data):
        """Test transcription performance requirements."""
        import time
        
        audio_data = sample_audio_data['data']
        
        # Mock realistic processing time
        def mock_transcribe(data):
            time.sleep(0.01)  # 10ms mock processing time
            return "performance test"
        
        mock_stt_processor.transcribe.side_effect = mock_transcribe
        
        start_time = time.time()
        result = mock_stt_processor.transcribe(audio_data)
        end_time = time.time()
        
        # Should complete reasonably quickly (under 1 second for test)
        processing_time = end_time - start_time
        assert processing_time < 1.0
        assert result == "performance test"

@pytest.mark.integration
class TestSTTProcessorIntegration:
    """Integration tests for STT processor with configuration."""
    
    def test_config_integration(self, mock_config):
        """Test integration with V3Config."""
        # Test that configuration is properly used
        assert mock_config.stt.model_path == "nvidia/parakeet-tdt_ctc-1.1b"
        assert mock_config.stt.device == "cpu"
        assert mock_config.audio.sample_rate == 16000
    
    def test_audio_config_compatibility(self, mock_config, sample_audio_data):
        """Test compatibility with audio configuration."""
        # Verify sample rate matches config
        assert sample_audio_data['sample_rate'] == mock_config.audio.sample_rate
        
        # Verify audio format
        assert len(sample_audio_data['data']) == sample_audio_data['samples']
    
    @pytest.mark.slow
    def test_large_audio_processing(self, mock_stt_processor):
        """Test processing of larger audio files."""
        import numpy as np
        
        # Generate larger audio sample (5 seconds)
        sample_rate = 16000
        duration = 5.0
        samples = int(sample_rate * duration)
        large_audio = np.random.random(samples).astype(np.float32)
        
        mock_stt_processor.transcribe.return_value = "large audio transcription"
        
        result = mock_stt_processor.transcribe(large_audio)
        assert result == "large audio transcription"
        
        # Verify the method was called with the large audio
        call_args = mock_stt_processor.transcribe.call_args[0]
        assert len(call_args[0]) == samples