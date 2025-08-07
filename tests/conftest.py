"""Pytest configuration and fixtures for PersonalParakeet tests."""

import asyncio
import sys
from pathlib import Path
from typing import Generator

import pytest
import torch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.core import HardwareValidator, TestReporter

# Global test reporter
_test_reporter = TestReporter()


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "hardware: mark test as requiring real hardware")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "interactive: mark test as requiring human interaction")
    config.addinivalue_line("markers", "benchmark: mark test as performance benchmark")
    config.addinivalue_line("markers", "stress: mark test as stress test")
    config.addinivalue_line("markers", "gpu_intensive: mark test as GPU-intensive")
    config.addinivalue_line("markers", "slow: mark test as slow-running")
    # Ensure 'unit' is registered so CI selection -m "unit and not slow" works
    config.addinivalue_line("markers", "unit: mark test as a fast unit test")


def pytest_sessionstart(session):
    """Run at the start of test session."""
    print("\n" + "=" * 70)
    print("PersonalParakeet Hardware Test Suite")
    print("=" * 70)

    # Validate hardware
    validator = HardwareValidator()
    print("\n" + validator.generate_report())
    print("=" * 70 + "\n")


def pytest_sessionfinish(session, exitstatus):
    """Run at the end of test session."""
    _test_reporter.print_summary()


@pytest.fixture(scope="session")
def hardware_validator() -> HardwareValidator:
    """Provide hardware validator instance."""
    return HardwareValidator()


@pytest.fixture(scope="session")
def test_reporter() -> TestReporter:
    """Provide test reporter instance."""
    return _test_reporter


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def audio_test_device(hardware_validator):
    """Get audio device for testing."""
    audio_info = hardware_validator.validate_audio()
    if not audio_info["available"]:
        pytest.skip("No audio devices available")
    return audio_info["default_device"]


@pytest.fixture
def gpu_device(hardware_validator):
    """Get GPU device for testing."""
    gpu_info = hardware_validator.validate_gpu()
    if not gpu_info["available"]:
        pytest.skip("No GPU available")
    return 0  # Default to first GPU


@pytest.fixture
def test_audio_files() -> dict:
    """Provide paths to test audio files."""
    fixtures_dir = Path(__file__).parent / "fixtures" / "audio"

    return {
        "hello_world": fixtures_dir / "hello_world.wav",
        "commands": fixtures_dir / "commands.wav",
        "continuous_speech": fixtures_dir / "continuous_speech.wav",
    }


@pytest.fixture(autouse=True)
def cleanup_gpu():
    """Clean up GPU memory after each test."""
    yield
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


@pytest.fixture
def skip_if_no_gpu(hardware_validator):
    """Skip test if no GPU available."""
    gpu_info = hardware_validator.validate_gpu()
    if not gpu_info["available"]:
        pytest.skip("GPU required but not available")


@pytest.fixture
def skip_if_windows_only():
    """Skip test if not on Windows."""""
    import platform

    if platform.system() != "Windows":
        pytest.skip("Windows-only test")


@pytest.fixture
def skip_if_slow_hardware(hardware_validator):
    """Skip test on slow hardware."""
    gpu_info = hardware_validator.validate_gpu()
    if gpu_info["available"] and gpu_info["devices"]:
        if gpu_info["devices"][0]["memory_gb"] < 4.0:
            pytest.skip("Insufficient GPU memory (<4GB)")
    else:
        pytest.skip("No GPU available")


# Test configuration
@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        "audio": {"sample_rate": 16000, "channels": 1, "chunk_size": 1024, "format": "int16"},
        "stt": {
            "model_size": "base",
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "compute_type": "float16" if torch.cuda.is_available() else "float32",
        },
        "timeouts": {"audio_init": 5.0, "model_load": 30.0, "transcription": 10.0},
        "tolerances": {
            "audio_level": 0.1,  # ±10%
            "latency": 0.2,  # ±20%
            "accuracy": 0.9,  # 90% minimum
        },
    }
