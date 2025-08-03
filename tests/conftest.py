"""
Test configuration and shared fixtures for PersonalParakeet v3 test suite.

This module provides common fixtures, mocks, and utilities used across
the test suite for PersonalParakeet v3 Flet-based implementation.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock
import numpy as np
import threading
import time

# Add project root to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "v3-flet"))

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_audio_device():
    """Mock audio device for testing audio processing."""
    mock = MagicMock()
    mock.sample_rate = 16000
    mock.channels = 1
    mock.dtype = np.float32
    
    def mock_record(duration, samplerate=None):
        """Generate mock audio data."""
        samples = int((samplerate or mock.sample_rate) * duration)
        return np.random.randn(samples).astype(np.float32)
    
    mock.record = mock_record
    return mock

@pytest.fixture
def mock_stt_engine():
    """Mock STT engine for testing speech-to-text processing."""
    mock = MagicMock()
    
    def mock_transcribe(audio_data):
        """Mock transcription with configurable responses."""
        if len(audio_data) > 0:
            return "This is a test transcription."
        return ""
    
    mock.transcribe = mock_transcribe
    mock.supported_formats = ["wav", "mp3", "flac"]
    return mock

@pytest.fixture
def mock_clipboard():
    """Mock clipboard manager for testing clipboard operations."""
    mock = MagicMock()
    mock.text = ""
    
    def mock_copy(text):
        mock.text = text
    
    def mock_paste():
        return mock.text
    
    mock.copy = mock_copy
    mock.paste = mock_paste
    return mock

@pytest.fixture
def mock_flet_app():
    """Mock Flet application for testing GUI components."""
    mock = MagicMock()
    mock.page = MagicMock()
    mock.page.window_width = 800
    mock.page.window_height = 600
    mock.page.theme = MagicMock()
    mock.page.controls = []
    return mock

@pytest.fixture
def sample_audio_data():
    """Generate sample audio data for testing."""
    duration = 1.0  # 1 second
    sample_rate = 16000
    samples = int(sample_rate * duration)
    
    # Generate synthetic speech-like audio
    t = np.linspace(0, duration, samples)
    frequency = 440  # A4 note
    audio = np.sin(2 * np.pi * frequency * t) * 0.3
    audio += np.random.randn(samples) * 0.01  # Add noise
    
    return audio.astype(np.float32)

@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        "audio": {
            "sample_rate": 16000,
            "channels": 1,
            "chunk_size": 1024,
            "format": "float32"
        },
        "stt": {
            "engine": "mock",
            "language": "en-US",
            "confidence_threshold": 0.8
        },
        "vad": {
            "aggressiveness": 3,
            "frame_duration_ms": 30
        }
    }

@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Set up test environment variables and mocks."""
    # Mock environment variables
    monkeypatch.setenv("PARAKEET_TEST_MODE", "true")
    monkeypatch.setenv("PARAKEET_MOCK_AUDIO", "true")
    
    # Ensure test data directory exists
    test_data_dir = Path(__file__).parent / "fixtures" / "data"
    test_data_dir.mkdir(parents=True, exist_ok=True)