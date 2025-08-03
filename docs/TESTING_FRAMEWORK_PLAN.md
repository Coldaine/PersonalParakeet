# PersonalParakeet Testing Framework Implementation Plan

## Overview
Complete rebuild of testing framework using ONLY real hardware - no mocks, stubs, or simulations.

## Core Principles
1. **Real Hardware Only** - All tests use actual microphone, GPU, and system resources
2. **Deterministic Where Possible** - Use pre-recorded audio samples for repeatable STT tests
3. **Human-in-Loop Support** - Interactive tests for features requiring human input
4. **Resource Management** - Proper setup/teardown of hardware resources
5. **Performance Awareness** - Track and report hardware utilization

## Directory Structure
```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── core/                    # Base infrastructure
│   ├── __init__.py
│   ├── base_hardware_test.py
│   ├── hardware_validator.py
│   ├── resource_monitor.py
│   └── test_reporter.py
├── fixtures/               # Test data
│   └── audio/             # Pre-recorded speech samples
│       ├── hello_world.wav
│       ├── commands.wav
│       └── continuous_speech.wav
├── hardware/              # Component tests
│   ├── __init__.py
│   ├── test_audio_capture.py
│   ├── test_stt_models.py
│   ├── test_gpu_cuda.py
│   └── test_window_detection.py
├── integration/           # Pipeline tests
│   ├── __init__.py
│   ├── test_audio_to_stt.py
│   ├── test_stt_to_injection.py
│   └── test_full_pipeline.py
├── interactive/           # Human-required tests
│   ├── __init__.py
│   ├── test_live_dictation.py
│   ├── test_app_switching.py
│   └── dashboard.py
├── benchmarks/           # Performance tests
│   ├── __init__.py
│   ├── test_stt_latency.py
│   ├── test_gpu_usage.py
│   └── test_memory_patterns.py
└── config.yaml           # Hardware-specific settings
```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
1. **BaseHardwareTest Class**
   - Hardware initialization/cleanup
   - Resource management
   - Error handling for hardware failures
   - Test isolation mechanisms

2. **Hardware Validator**
   - Check GPU/CUDA availability
   - Verify microphone access
   - Validate system capabilities
   - Generate hardware report

3. **Test Configuration**
   - Hardware-specific tolerances
   - Performance baselines
   - Resource limits

### Phase 2: Component Tests (Week 2)
1. **Audio Hardware Tests**
   - Microphone enumeration
   - Audio capture quality
   - Buffer handling
   - Sample rate validation
   - Noise floor measurement

2. **STT Model Tests**
   - Model loading time
   - Inference accuracy
   - GPU memory usage
   - Batch processing
   - Error recovery

3. **System Integration Tests**
   - Window detection accuracy
   - Text injection reliability
   - Multi-platform compatibility

### Phase 3: Integration Tests (Week 3)
1. **Pipeline Tests**
   - Audio → STT latency
   - STT → Injection accuracy
   - End-to-end reliability
   - Concurrent operations

2. **Interactive Test Suite**
   - Live dictation scenarios
   - Application switching
   - Error recovery
   - User feedback loops

### Phase 4: Performance & Reliability (Week 4)
1. **Benchmarks**
   - Transcription speed
   - Resource utilization
   - Memory patterns
   - Long-running stability

2. **Stress Tests**
   - Continuous operation
   - Resource exhaustion
   - Recovery mechanisms

## Key Components

### BaseHardwareTest Class
```python
class BaseHardwareTest:
    """Base class for all hardware tests"""
    
    @classmethod
    def setup_class(cls):
        """Initialize hardware resources"""
        cls.validate_hardware()
        cls.initialize_audio()
        cls.initialize_gpu()
    
    @classmethod
    def teardown_class(cls):
        """Clean up hardware resources"""
        cls.cleanup_audio()
        cls.cleanup_gpu()
    
    def setup_method(self):
        """Per-test setup"""
        self.start_resource_monitoring()
    
    def teardown_method(self):
        """Per-test cleanup"""
        self.stop_resource_monitoring()
        self.generate_test_report()
```

### Test Categories
1. **Unit Tests** (`@pytest.mark.hardware`)
   - Single component validation
   - Hardware capability checks
   - Basic functionality

2. **Integration Tests** (`@pytest.mark.integration`)
   - Multi-component workflows
   - Pipeline validation
   - Error propagation

3. **Interactive Tests** (`@pytest.mark.interactive`)
   - Require human input
   - Visual/audio feedback
   - Manual validation

4. **Performance Tests** (`@pytest.mark.benchmark`)
   - Latency measurements
   - Throughput testing
   - Resource profiling

5. **Stress Tests** (`@pytest.mark.stress`)
   - Long-running scenarios
   - Resource limits
   - Stability validation

## Handling Hardware Variability

### Tolerance Ranges
- Audio levels: ±10% variance allowed
- STT latency: Baseline ±20% acceptable
- GPU memory: Track relative usage, not absolute

### Retry Logic
```python
@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def initialize_hardware():
    """Retry hardware initialization with backoff"""
    pass
```

### Hardware Profiles
```yaml
profiles:
  high_end:
    gpu_memory: ">8GB"
    expected_latency: "<100ms"
  standard:
    gpu_memory: "4-8GB"
    expected_latency: "<200ms"
  minimum:
    gpu_memory: "2-4GB"
    expected_latency: "<500ms"
```

## Test Execution

### Running Tests
```bash
# All tests
pytest tests/

# Only hardware unit tests
pytest tests/hardware/ -m hardware

# Interactive tests with dashboard
python tests/interactive/dashboard.py

# Performance benchmarks
pytest tests/benchmarks/ -m benchmark --benchmark-only

# Skip GPU-intensive tests
pytest tests/ -m "not gpu_intensive"
```

### CI/CD Considerations
- Separate test suites for CI vs local
- Document hardware requirements
- Provide fallback for missing hardware
- Clear skip messages for unavailable tests

## Success Criteria
1. All tests run on real hardware
2. No mocking or stubbing
3. Clear documentation of hardware requirements
4. Reliable test execution
5. Meaningful performance baselines
6. Easy to run and understand

## Timeline
- Week 1: Core infrastructure
- Week 2: Component tests  
- Week 3: Integration tests
- Week 4: Performance & polish
- Total: 4 weeks to complete framework

## Next Steps
1. Create base test infrastructure
2. Set up hardware validation
3. Implement first audio capture test
4. Iterate based on real hardware behavior