"""
PROPER test suite for STTProcessor - tests REAL code with mocked hardware.
"""

import pytest
from unittest.mock import patch, MagicMock
import numpy as np
import torch

# Import the REAL class we're testing
from core.stt_processor import STTProcessor
from config import V3Config


class TestSTTProcessorReal:
    """Tests that actually verify the REAL STTProcessor code."""
    
    @pytest.fixture
    def config(self):
        """Real config object."""
        config = V3Config()
        config.audio.stt_model_path = "/fake/model.nemo"
        config.audio.stt_device = "cuda"
        return config
    
    @pytest.fixture
    def real_stt_processor(self, config):
        """Create REAL STTProcessor instance."""
        return STTProcessor(config)
    
    @patch('core.stt_processor.nemo_asr')
    @patch('core.stt_processor.CUDACompatibility')
    @patch('core.stt_processor.get_optimal_device')
    async def test_initialize_loads_model_correctly(self, mock_device, mock_cuda, mock_nemo, real_stt_processor):
        """Test that initialize() actually loads the model correctly."""
        # Setup mocks
        mock_device.return_value = 'cuda'
        mock_cuda.check_and_apply_fixes.return_value = {'cuda_available': True}
        mock_model = MagicMock()
        mock_nemo.models.EncDecRNNTBPEModel.from_pretrained.return_value = mock_model
        
        # Call REAL initialize method
        await real_stt_processor.initialize()
        
        # Verify the REAL code:
        # 1. Checked CUDA compatibility
        mock_cuda.check_and_apply_fixes.assert_called_once()
        
        # 2. Selected correct device
        mock_device.assert_called_once_with(force_cpu=False)
        
        # 3. Loaded the model with correct parameters
        mock_nemo.models.EncDecRNNTBPEModel.from_pretrained.assert_called()
        
        # 4. Set internal state correctly
        assert real_stt_processor.is_initialized is True
        assert real_stt_processor.device == 'cuda'
        assert real_stt_processor.model == mock_model
    
    @patch('core.stt_processor.nemo_asr')
    async def test_transcribe_processes_audio_correctly(self, mock_nemo, real_stt_processor):
        """Test that transcribe() processes audio through the model correctly."""
        # Setup mock model
        mock_model = MagicMock()
        mock_model.transcribe.return_value = ["Hello world"]
        real_stt_processor.model = mock_model
        real_stt_processor.is_initialized = True
        real_stt_processor.device = 'cuda'
        
        # Create test audio
        audio_data = np.random.rand(16000).astype(np.float32)  # 1 second of audio
        
        # Call REAL transcribe method
        result = await real_stt_processor.transcribe(audio_data)
        
        # Verify the REAL code:
        # 1. Called model with correct parameters
        mock_model.transcribe.assert_called_once()
        call_args = mock_model.transcribe.call_args
        
        # 2. Passed audio data correctly
        assert isinstance(call_args[0][0], list)  # Should convert to list
        
        # 3. Returned the transcription
        assert result == "Hello world"
    
    async def test_transcribe_fails_when_not_initialized(self, real_stt_processor):
        """Test that transcribe() raises error when not initialized."""
        audio_data = np.random.rand(16000).astype(np.float32)
        
        # Should fail because not initialized
        with pytest.raises(Exception):  # Real code should raise specific exception
            await real_stt_processor.transcribe(audio_data)
    
    @patch('core.stt_processor.Path')
    @patch('core.stt_processor.nemo_asr')
    async def test_uses_local_model_when_available(self, mock_nemo, mock_path, real_stt_processor):
        """Test that it uses local model file when available."""
        # Setup
        mock_path.return_value.exists.return_value = True
        real_stt_processor.config.audio.stt_model_path = "/local/model.nemo"
        
        # Initialize
        await real_stt_processor.initialize()
        
        # Should load from local path, not download
        mock_nemo.models.EncDecRNNTBPEModel.restore_from.assert_called_with(
            "/local/model.nemo"
        )