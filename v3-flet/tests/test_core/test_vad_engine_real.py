"""
REAL tests for VAD Engine that actually test the code, not mocks.
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
import torch

# Import the REAL class we're testing
from core.vad_engine import VADEngine
from config import V3Config


class TestVADEngineReal:
    """Tests that actually verify the REAL VADEngine code."""
    
    @pytest.fixture
    def config(self):
        """Real config object."""
        return V3Config()
    
    @pytest.fixture
    def real_vad_engine(self, config):
        """Create REAL VADEngine instance."""
        return VADEngine(config)
    
    @patch('core.vad_engine.torch.hub.load')
    def test_initialize_loads_silero_model(self, mock_hub_load, real_vad_engine):
        """Test that initialize() actually loads the Silero VAD model."""
        # Setup mock for torch.hub.load ONLY
        fake_model = MagicMock()
        mock_hub_load.return_value = fake_model
        
        # Call REAL initialize method
        real_vad_engine.initialize()
        
        # Verify REAL code behavior:
        # 1. Called torch.hub.load with correct parameters
        mock_hub_load.assert_called_once_with(
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            onnx=False
        )
        
        # 2. Stored the model correctly
        assert real_vad_engine.model == fake_model
        assert real_vad_engine.is_initialized is True
    
    def test_is_speech_with_real_logic(self, real_vad_engine):
        """Test is_speech with actual VAD logic (no model needed)."""
        # Test the preprocessing logic even without model
        
        # Test 1: Empty audio should return False
        empty_audio = np.array([])
        result = real_vad_engine.is_speech(empty_audio)
        assert result['speech'] is False
        assert result['confidence'] == 0.0
        
        # Test 2: Very quiet audio should return False
        quiet_audio = np.random.rand(16000) * 0.001  # Very quiet
        result = real_vad_engine.is_speech(quiet_audio)
        assert result['speech'] is False
        
    @patch('core.vad_engine.torch.hub.load')
    def test_is_speech_processes_audio_correctly(self, mock_hub_load, real_vad_engine):
        """Test that is_speech processes audio through the model correctly."""
        # Create a fake model that returns speech probabilities
        fake_model = MagicMock()
        fake_model.return_value = torch.tensor([[0.8]])  # 80% speech confidence
        mock_hub_load.return_value = fake_model
        
        # Initialize with mocked model
        real_vad_engine.initialize()
        
        # Create test audio (1 second at 16kHz)
        audio_data = np.random.rand(16000).astype(np.float32)
        
        # Call REAL is_speech method
        result = real_vad_engine.is_speech(audio_data)
        
        # Verify REAL code behavior:
        # 1. Model was called with tensor
        assert fake_model.called
        call_args = fake_model.call_args[0][0]
        assert isinstance(call_args, torch.Tensor)
        assert call_args.shape == (1, 16000)  # Correct shape
        
        # 2. Result has correct structure
        assert 'speech' in result
        assert 'confidence' in result
        assert result['speech'] is True  # 0.8 > threshold
        assert result['confidence'] == 0.8
    
    def test_reset_states_clears_model(self, real_vad_engine):
        """Test that reset_states actually clears the model state."""
        # Setup
        real_vad_engine.model = MagicMock()
        real_vad_engine.model.reset_states = MagicMock()
        real_vad_engine.is_initialized = True
        
        # Call REAL reset_states
        real_vad_engine.reset_states()
        
        # Verify it called model's reset_states
        real_vad_engine.model.reset_states.assert_called_once()
    
    @patch('core.vad_engine.logger')
    def test_handles_initialization_error(self, mock_logger, real_vad_engine):
        """Test that initialization errors are handled properly."""
        with patch('core.vad_engine.torch.hub.load') as mock_load:
            mock_load.side_effect = Exception("Network error")
            
            # Should not crash
            real_vad_engine.initialize()
            
            # Should log error
            mock_logger.error.assert_called()
            
            # Should not be initialized
            assert real_vad_engine.is_initialized is False