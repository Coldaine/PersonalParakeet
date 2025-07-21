# Task Completion Checklist - PersonalParakeet v2

## When a Development Task is Completed

### 1. Code Quality Checks
```bash
# Format code (if dev dependencies available)
black --line-length 100 .
isort --profile black .

# Type checking
mypy personalparakeet/
```

### 2. v2 System Testing Requirements
```bash
# CRITICAL: Test audio hardware compatibility
python tests/test_audio_minimal.py

# Test core STT functionality  
python personalparakeet/dictation.py

# Test Clarity Engine corrections
python personalparakeet/clarity_engine.py

# Test complete v2 system (manual verification preferred)
python start_dictation_view.py
```

### 3. Frontend Testing (Tauri/React)
```bash
# Install/update UI dependencies
cd dictation-view-ui && npm install

# Test UI in development mode
cd dictation-view-ui && npm run tauri dev

# Build UI for production testing
cd dictation-view-ui && npm run tauri build
```

### 4. WebSocket Communication Testing
```bash
# Test WebSocket server independently
python dictation_websocket_bridge.py

# Test WebSocket fixes if needed
python test_websocket_fixes.py

# Verify real-time communication between frontend/backend
```

### 5. Platform Verification
- **Windows**: Ensure full Dictation View functionality with transparent UI
- **Audio Compatibility**: Verify sounddevice works with current system
- **GPU Support**: Check CUDA compatibility if relevant changes made
- **UI Responsiveness**: Test Tauri UI responsiveness and transparency effects

### 6. Environment Health Check
```bash
# Verify Python version consistency (expect 3.11+ per .python-version)
python --version

# Check if venv needed and working
# Note: Currently no .venv - may need creation for dependency isolation

# Verify core dependencies are available
python -c "import torch, sounddevice, websockets; print('Core deps OK')"
```

### 7. Performance Verification
```bash
# GPU monitoring during testing
nvidia-smi

# WebSocket latency testing
# Check audio capture and transcription latency
# Verify UI update responsiveness
```

### 8. Integration Testing
- **Complete Workflow**: Start system → Audio capture → Transcription → UI display
- **Clarity Engine**: Test text corrections in real-time
- **Voice Activity Detection**: Verify pause detection and auto-commit
- **Error Recovery**: Test graceful handling of connection issues

### 9. Never Automatically Commit
- Manual review required for all changes
- User must explicitly request git commits
- Preserve development history and decision rationale

## Current Priority: Establish Clean Development Environment
- Consider creating Python 3.11 virtual environment for dependency isolation
- Ensure all v2 components (Python backend + Tauri frontend) work together
- Verify WebSocket communication stability