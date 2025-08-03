# PersonalParakeet Testing Framework

A comprehensive hardware-based testing framework for PersonalParakeet that uses **ONLY real hardware** - no mocks, stubs, or simulations.

## Overview

This testing framework is designed to test PersonalParakeet's real-time dictation system using actual hardware components:
- Real microphones for audio capture
- GPU/CUDA for speech recognition
- System resources for performance testing
- Actual window detection and text injection

## Quick Start

```bash
# Run all tests
pytest tests/

# Run only hardware tests
pytest tests/ -m hardware

# Run integration tests
pytest tests/ -m integration

# Run quick tests (exclude slow/GPU-intensive)
pytest tests/ -m "not slow and not gpu_intensive"

# Run with detailed output
pytest tests/ -v

# Use the test runner script
python tests/run_tests.py --hardware --verbose
```

## Test Categories

### 1. Hardware Tests (`@pytest.mark.hardware`)
Basic hardware component validation:
- Audio device enumeration and capture
- STT model loading and inference
- GPU/CUDA functionality
- Window detection capabilities

```bash
pytest tests/hardware/
```

### 2. Integration Tests (`@pytest.mark.integration`)
Multi-component pipeline tests:
- Audio capture → STT transcription
- STT output → text injection
- Full end-to-end pipeline

```bash
pytest tests/integration/
```

### 3. Interactive Tests (`@pytest.mark.interactive`)
Tests requiring human interaction:
- Live speech recognition
- Continuous dictation
- Noise handling evaluation

```bash
pytest tests/interactive/
```

### 4. Performance Benchmarks (`@pytest.mark.benchmark`)
Performance and latency measurements:
- STT model latency
- GPU utilization
- Memory usage patterns
- Sustained throughput

```bash
pytest tests/benchmarks/
```

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── config.yaml              # Hardware-specific settings
├── run_tests.py            # Test runner script
├── README.md               # This file
│
├── core/                   # Base infrastructure
│   ├── __init__.py
│   ├── base_hardware_test.py    # Base test class
│   ├── hardware_validator.py    # Hardware validation
│   ├── resource_monitor.py      # Resource monitoring
│   └── test_reporter.py         # Test reporting
│
├── fixtures/              # Test data
│   └── audio/            # Pre-generated audio samples
│       ├── hello_world.wav
│       ├── commands.wav
│       ├── continuous_speech.wav
│       ├── silence.wav
│       └── test_tone.wav
│
├── hardware/             # Component tests
│   ├── __init__.py
│   ├── test_audio_capture.py
│   ├── test_stt_models.py
│   ├── test_gpu_cuda.py
│   └── test_window_detection.py
│
├── integration/          # Pipeline tests
│   ├── __init__.py
│   ├── test_audio_to_stt.py
│   ├── test_stt_to_injection.py
│   └── test_full_pipeline.py
│
├── interactive/          # Human-required tests
│   ├── __init__.py
│   └── test_live_dictation.py
│
└── benchmarks/           # Performance tests
    ├── __init__.py
    └── test_stt_latency.py
```

## Hardware Requirements

### Minimum Requirements
- Microphone (any input device)
- 2GB+ GPU memory (or CPU fallback)
- Python 3.8+
- PyAudio-compatible audio system

### Recommended Requirements
- USB microphone or headset
- NVIDIA GPU with 4GB+ memory
- CUDA 11.0+
- Low-latency audio drivers

## Running Specific Test Suites

### Audio Hardware Tests
```bash
# Test audio capture functionality
pytest tests/hardware/test_audio_capture.py -v

# Skip if no audio devices
pytest tests/hardware/test_audio_capture.py -v --no-audio
```

### GPU Tests
```bash
# Test GPU/CUDA functionality
pytest tests/hardware/test_gpu_cuda.py -v

# Skip GPU tests on CPU-only systems
pytest tests/ -m "not gpu_intensive"
```

### Interactive Tests
```bash
# Run interactive speech tests
pytest tests/interactive/test_live_dictation.py -v -s

# The -s flag shows print output for instructions
```

### Performance Benchmarks
```bash
# Run all benchmarks
pytest tests/benchmarks/ -v

# Run specific benchmark
pytest tests/benchmarks/test_stt_latency.py::test_whisper_model_latencies -v
```

## Test Configuration

### config.yaml
Defines hardware profiles and test parameters:
```yaml
profiles:
  high_end:
    gpu_memory: ">8GB"
    expected_latency: "<100ms"
  standard:
    gpu_memory: "4-8GB"
    expected_latency: "<200ms"
```

### Environment Variables
```bash
# Skip GPU tests
export PERSONALPARAKEET_NO_GPU=1

# Set custom audio device
export PERSONALPARAKEET_AUDIO_DEVICE=2

# Enable debug output
export PERSONALPARAKEET_DEBUG=1
```

## Test Reports

Test results are automatically saved to `test_reports/`:
- `test_report_YYYYMMDD_HHMMSS.json` - Detailed JSON report
- `test_report_YYYYMMDD_HHMMSS.txt` - Human-readable summary

Generate HTML report:
```bash
pytest tests/ --html=test_reports/report.html --self-contained-html
```

## Writing New Tests

### Basic Hardware Test
```python
from tests.core import BaseHardwareTest
import pytest

class TestMyHardware(BaseHardwareTest):
    @pytest.mark.hardware
    def test_my_feature(self):
        # Hardware is automatically initialized
        assert self.audio_device is not None
        
        # Use hardware validation
        self.assert_hardware_available("gpu")
        
        # Your test code here
```

### Integration Test
```python
@pytest.mark.integration
def test_pipeline(audio_test_device):
    # Use fixtures for common setup
    # Test multi-component workflows
    pass
```

## Troubleshooting

### No Audio Devices Found
```bash
# Check audio devices
python -c "import pyaudio; p=pyaudio.PyAudio(); print(p.get_device_count())"
```

### GPU Not Detected
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

### Tests Running Slowly
```bash
# Run only quick tests
pytest tests/ -m "not slow" -v

# Use smaller models for testing
export PERSONALPARAKEET_TEST_MODEL=tiny
```

## CI/CD Integration

For CI environments without hardware:
```bash
# Skip hardware-dependent tests
pytest tests/ -m "not hardware and not gpu_intensive" -v

# Run only unit tests
pytest tests/ -m "unit" -v
```

## Contributing

When adding new tests:
1. Use real hardware - no mocking
2. Add appropriate markers (@pytest.mark.hardware, etc.)
3. Include resource cleanup in teardown
4. Document hardware requirements
5. Provide fallback for missing hardware

## License

Same as PersonalParakeet project.