# PersonalParakeet v3 - Testing Guide

## Overview
PersonalParakeet uses a comprehensive hardware-based testing framework that uses ONLY real hardware components—no mocks, stubs, or simulations. All tests run on actual microphones, GPUs, and system resources.

## Core Testing Principles
1. **Real Hardware Only** - All tests use actual microphone, GPU, and system resources
2. **Deterministic Where Possible** - Use pre-recorded audio samples for repeatable STT tests
3. **Human-in-Loop Support** - Interactive tests for features requiring human input
4. **Resource Management** - Proper setup/teardown of hardware resources
5. **Performance Awareness** - Track and report hardware utilization

## Test Categories

### Hardware Tests (`tests/hardware/`)
- **Audio Capture**: `test_audio_capture.py` - Validates microphone functionality
- **GPU/CUDA**: `test_gpu_cuda.py` - Tests GPU acceleration and CUDA availability
- **Window Detection**: `test_window_detection.py` - Tests system window interaction

### Integration Tests (`tests/integration/`)
- **STT Pipeline**: End-to-end speech-to-text processing
- **Full Pipeline**: Complete audio → STT → text injection workflow

### Unit Tests (`tests/unit/`)
- **Configuration**: `test_config.py` - Configuration system tests
- **Components**: Individual component testing (thought linker, etc.)

### Interactive Tests (`tests/interactive/`)
- Human-in-the-loop tests requiring user interaction

## Running Tests

### All Tests
```bash
# Activate environment first
conda activate personalparakeet

# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v --tb=short
```

### Specific Test Categories
```bash
# Hardware validation
poetry run pytest -m hardware

# Integration tests
poetry run pytest -m integration

# Unit tests only
poetry run pytest -m unit

# Interactive tests (requires human input)
poetry run pytest -m interactive
```

### Test Markers
- `unit`: Unit tests (isolated components)
- `integration`: End-to-end integration tests  
- `hardware`: Hardware validation tests
- `interactive`: Tests requiring human interaction
- `slow`: Tests taking more than 10 seconds
- `gpu_intensive`: GPU-intensive tests

## Test Infrastructure

### Core Components
- **BaseHardwareTest**: Base class for hardware-dependent tests
- **HardwareValidator**: Validates hardware availability before tests
- **ResourceMonitor**: Tracks hardware resource usage during tests
- **TestReporter**: Generates detailed test reports with system info

### Test Reports
Test execution generates detailed reports in `test_reports/`:
- JSON format for programmatic analysis
- Human-readable text format
- Hardware configuration details
- Performance metrics

### Test Configuration
- `tests/config.yaml` - Test-specific configuration
- `pytest.ini` - Pytest configuration with markers and options
- Environment-specific settings via `tests/conftest.py`

## Audio Testing

### Pre-recorded Audio Fixtures
Located in `tests/fixtures/audio/`:
- `hello_world.wav` - Basic STT test
- `commands.wav` - Command recognition test
- `continuous_speech.wav` - Long-form dictation test
- `silence.wav` - VAD silence detection test
- `test_tone.wav` - Audio hardware validation

### Live Audio Testing
```bash
# Terminal audio monitor
poetry run python src/personalparakeet/tests/utilities/test_live_audio.py

# GUI audio monitor
poetry run python src/personalparakeet/tests/utilities/test_live_audio_gui.py
```

## Hardware Requirements
- **Microphone**: Physical microphone required (no simulation)
- **GPU**: NVIDIA GPU recommended for ML tests
- **Audio System**: Functional audio input/output
- **Window System**: GUI environment for window detection tests

## Troubleshooting

### Common Issues
1. **No microphone detected**: Check hardware connections and permissions
2. **CUDA not available**: Verify NVIDIA drivers and CUDA installation
3. **Permission errors**: Ensure microphone permissions granted
4. **Audio device busy**: Close other applications using audio

### Debug Commands
```bash
# Check hardware availability
python scripts/validate_environment.py

# Test GPU
python scripts/gpu_test.py

# Audio device diagnostics
poetry run python tests/hardware/test_audio_capture.py -v
```

## Test Development Guidelines
- Always test with real hardware
- Use pre-recorded fixtures for deterministic results
- Include proper setup/teardown for hardware resources
- Add appropriate test markers for categorization
- Generate meaningful test reports with system context