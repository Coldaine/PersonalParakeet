# Task Completion Checklist

## When a Development Task is Completed

### 1. Code Quality Checks
```bash
# Format code (if dev dependencies available)
black --line-length 100 .
isort --profile black .

# Type checking
mypy personalparakeet/
```

### 2. Testing Requirements
```bash
# CRITICAL: Test audio hardware compatibility
python tests/test_audio_minimal.py

# Test LocalAgreement core logic
python tests/test_local_agreement.py

# Test system integration
python tests/test_keyboard_output.py

# Full system test (manual verification preferred)
python run_dictation.py
```

### 3. Platform Verification
- **Windows**: Ensure full dictation functionality with native text injection
- **Audio Compatibility**: Verify sounddevice works with current system
- **GPU Support**: Check CUDA compatibility if relevant changes made

### 4. Documentation Updates
- Update README.md if functionality changes
- Update CLAUDE.md with any development constraint changes
- Maintain working system status confirmation

### 5. Virtual Environment Health
- Ensure pip list works without errors
- Verify Python version consistency (3.11.x)
- Check that all required dependencies are installed

### 6. Performance Verification
```bash
# GPU monitoring during testing
nvidia-smi

# System resource monitoring
# Check audio latency and processing performance
```

### 7. Never Automatically Commit
- Manual review required for all changes
- User must explicitly request git commits
- Preserve development history and decision rationale

## Current Priority: Fix Virtual Environment
Before any development work, the Python version mismatch must be resolved to restore basic functionality.