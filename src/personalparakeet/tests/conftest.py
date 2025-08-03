"""
PersonalParakeet v3 Test Configuration

Shared pytest fixtures and configuration for comprehensive testing
with hardware dependency mocking for CI/CD compatibility.
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Mock hardware dependencies before any imports
@pytest.fixture(scope="session", autouse=True)
def mock_hardware_dependencies():
    """Mock all hardware dependencies for CI/CD environments."""
    
    # Mock torch and CUDA
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False
    mock_torch.device.return_value = "cpu"
    
    # Mock NeMo components
    mock_nemo = MagicMock()
    mock_nemo_asr = MagicMock()
    mock_nemo_models = MagicMock()
    
    # Mock audio libraries
    mock_sounddevice = MagicMock()
    mock_pyaudio = MagicMock()
    mock_soundfile = MagicMock()
    
    # Mock system libraries
    mock_keyboard = MagicMock()
    mock_pynput = MagicMock()
    mock_pyperclip = MagicMock()
    
    with patch.dict('sys.modules', {
        'torch': mock_torch,
        'nemo': mock_nemo,
        'nemo.collections': mock_nemo,
        'nemo.collections.asr': mock_nemo_asr,
        'nemo.collections.asr.models': mock_nemo_models,
        'sounddevice': mock_sounddevice,
        'pyaudio': mock_pyaudio, 
        'soundfile': mock_soundfile,
        'keyboard': mock_keyboard,
        'pynput': mock_pynput,
        'pyperclip': mock_pyperclip,
    }):
        yield


from dataclasses import dataclass, field

@dataclass
class MockV3Config:
    """Mock configuration matching actual V3Config structure."""
    
    @dataclass
    class AudioConfig:
        sample_rate: int = 16000
        channels: int = 1
        chunk_size: int = 1024
        
    @dataclass
    class VADConfig:
        threshold: float = 0.5
        min_speech_duration: float = 0.1
        min_silence_duration: float = 0.5
        
    @dataclass
    class STTConfig:
        model_path: str = "nvidia/parakeet-tdt_ctc-1.1b"
        device: str = "cpu"
        
    audio: AudioConfig = field(default_factory=AudioConfig)
    vad: VADConfig = field(default_factory=VADConfig)
    stt: STTConfig = field(default_factory=STTConfig)


@pytest.fixture
def mock_config():
    """Provide mock configuration for testing."""
    return MockV3Config()


@pytest.fixture
def mock_audio_device():
    """Mock audio device for testing."""
    device = MagicMock()
    device.name = "Test Audio Device"
    device.max_input_channels = 2
    device.default_sample_rate = 16000
    return device


@pytest.fixture
def sample_audio_data():
    """Generate sample audio data for testing."""
    sample_rate = 16000
    duration = 1.0  # 1 second
    samples = int(sample_rate * duration)
    
    # Generate sine wave as sample audio
    t = np.linspace(0, duration, samples, False)
    frequency = 440  # A4 note
    audio_data = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    
    return {
        'data': audio_data,
        'sample_rate': sample_rate,
        'duration': duration,
        'samples': samples
    }


@pytest.fixture
def setup_test_environment(mock_config, mock_audio_device):
    """Set up complete test environment with all mocks."""
    
    # Mock environment variables
    test_env = {
        'PARAKEET_TEST_MODE': 'true',
        'PARAKEET_MOCK_AUDIO': 'true',
        'PARAKEET_DISABLE_GUI': 'true'
    }
    
    with patch.dict('os.environ', test_env):
        yield {
            'config': mock_config,
            'audio_device': mock_audio_device,
            'env': test_env
        }


@pytest.fixture
def mock_stt_processor(mock_config):
    """Create a mock STT processor for testing."""
    from unittest.mock import MagicMock
    
    processor = MagicMock()
    processor.initialize.return_value = None
    processor.transcribe.return_value = "test transcription"
    processor._transcribe_sync.return_value = "test transcription"
    processor.cleanup.return_value = None
    processor.config = mock_config.stt
    
    return processor


@pytest.fixture
def mock_vad_engine(mock_config):
    """Create a mock VAD engine for testing."""
    from unittest.mock import MagicMock
    
    vad = MagicMock()
    # Return proper dictionary structure for VAD results
    vad.process_audio_frame.return_value = {
        'is_speech': True,
        'confidence': 0.8,
        'rms_energy': 0.5
    }
    vad._calculate_rms_energy.return_value = 0.5
    vad.config = mock_config.vad
    vad.callbacks = []
    
    def mock_add_callback(callback_type, callback_func):
        vad.callbacks.append((callback_type, callback_func))
    
    vad.add_callback = mock_add_callback
    
    return vad


@pytest.fixture
def mock_audio_pipeline(mock_stt_processor, mock_vad_engine, mock_config):
    """Create a mock audio pipeline for integration testing."""
    from unittest.mock import MagicMock
    
    # Create mock audio component
    mock_audio = MagicMock()
    mock_audio.start_recording.return_value = None
    mock_audio.stop_recording.return_value = None
    
    # Update STT processor to return expected text
    mock_stt_processor.transcribe.return_value = "Hello world"
    
    # Update VAD engine to return high confidence for triggering STT
    mock_vad_engine.process_audio_frame.return_value = {
        'is_speech': True,
        'confidence': 0.8,  # Above 0.7 threshold
        'rms_energy': 0.6
    }
    
    # Return dictionary structure expected by tests
    return {
        'vad': mock_vad_engine,
        'stt': mock_stt_processor,
        'audio': mock_audio,
        'config': mock_config
    }


# Test markers for different test categories
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line("markers", "integration: Integration tests for component interaction") 
    config.addinivalue_line("markers", "e2e: End-to-end tests for complete workflows")
    config.addinivalue_line("markers", "performance: Performance and benchmark tests")
    config.addinivalue_line("markers", "slow: Tests that take longer than usual to run")
    config.addinivalue_line("markers", "hardware: Tests requiring specific hardware")
    config.addinivalue_line("markers", "manual: Manual tests requiring user interaction")


# Skip hardware tests in CI
def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip hardware tests in CI environments."""
    import os
    
    if os.getenv('CI') or os.getenv('GITHUB_ACTIONS'):
        skip_hardware = pytest.mark.skip(reason="Hardware tests skipped in CI")
        for item in items:
            if "hardware" in item.keywords:
                item.add_marker(skip_hardware)