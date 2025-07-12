# Parakeet Dictation System Test Plan

## Pre-Test Setup Checklist

### 1. Environment Setup
- [x] Python virtual environment created
- [x] All dependencies installed via requirements.txt
- [ ] CUDA drivers installed (for GPU acceleration)
- [ ] Microphone available and permissions granted
- [ ] Ollama installed and running
- [ ] Llama2 model pulled (`ollama pull llama2:7b`)

### 2. Component Tests (Automated)

Run with: `python automated_tests.py`

#### Audio Handler Tests
- Device detection and selection
- Sample rate configuration
- VAD model loading
- Audio stream initialization

#### Transcriber Tests  
- Model loading (CPU fallback if no GPU)
- Buffer management
- Context preservation
- Device selection

#### Text Output Tests
- Application detection
- Method selection logic
- Platform-specific handling

#### LLM Refiner Tests
- Ollama connectivity
- Context classification
- Error handling

### 3. Integration Tests (Semi-Automated)

Run with: `python integration_tests.py`

#### End-to-End Flow
- Audio capture → VAD → Transcription → Output
- Hotkey functionality
- WebSocket server mode
- GPU memory monitoring

### 4. Manual Testing Checklist

#### Basic Functionality
- [ ] Launch application: `python dictation.py`
- [ ] Press F4 to start dictation
- [ ] Speak test phrase: "Hello world, this is a test"
- [ ] Verify text appears in active window
- [ ] Press F4 to stop dictation

#### Advanced Features
- [ ] Test F5 to toggle LLM refinement
- [ ] Test F6 to toggle overlay display
- [ ] Test different applications (notepad, browser, terminal)
- [ ] Test WebSocket mode: `python dictation.py --server`
- [ ] Connect WebSocket client and verify streaming

#### Performance Testing
- [ ] Monitor GPU memory usage during operation
- [ ] Check transcription latency
- [ ] Verify VAD responsiveness
- [ ] Test continuous dictation for 5 minutes

### 5. Error Scenarios

#### Graceful Degradation
- [ ] No GPU available (should fallback to CPU)
- [ ] Ollama not running (should bypass refinement)
- [ ] No microphone (should show error)
- [ ] WebSocket client disconnection

### 6. Platform-Specific Tests

#### Windows
- [ ] Clipboard paste in various apps
- [ ] Window detection accuracy
- [ ] Hotkey registration

#### Linux
- [ ] X11 clipboard handling
- [ ] Application detection
- [ ] Audio device selection

## Test Results Template

```yaml
test_date: YYYY-MM-DD
tester: [Name]
environment:
  os: [Windows/Linux/macOS]
  python_version: [version]
  cuda_available: [yes/no]
  gpu_model: [model]
  
results:
  component_tests: [pass/fail]
  integration_tests: [pass/fail]
  manual_tests: [pass/fail]
  
issues_found:
  - description: 
    severity: [high/medium/low]
    steps_to_reproduce:
    
performance_metrics:
  transcription_latency_ms: 
  gpu_memory_usage_mb:
  words_per_minute:
```