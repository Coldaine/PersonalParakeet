# PersonalParakeet v3 Tests

## Structure

### `/integration`
Hardware integration tests that require GPU, CUDA, and microphone access.
These tests verify the actual system functionality.

### `/utilities`
Interactive test scripts for manual development and debugging:
- `test_live_audio.py` - Monitor microphone levels in real-time
- `test_full_pipeline.py` - Test complete audio → STT → injection pipeline
- `test_microphone.py` - Basic microphone functionality test
- `test_detector.py` - Window/application detection testing
- `test_injection.py` - Text injection testing
- `test_enhanced_injection.py` - Advanced injection strategies

## Running Tests

### Hardware Integration Tests
```bash
pytest tests/integration/ --hardware
```

### Interactive Utilities
```bash
python tests/utilities/test_live_audio.py
python tests/utilities/test_full_pipeline.py
```

## Note
This project requires NVIDIA GPU with CUDA support. Mock tests have been removed as they provided no value. All tests assume hardware availability.