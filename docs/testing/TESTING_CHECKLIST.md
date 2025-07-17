# PersonalParakeet Testing Checklist

## Pre-Test Setup Checklist

### Environment Setup
- [ ] Windows 10/11 system
- [ ] NVIDIA GPU with CUDA 12.1+ drivers
- [ ] Python 3.11 virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Microphone connected and working
- [ ] Run as Administrator (for keyboard injection)

### GPU Verification
- [ ] Run `nvidia-smi` - verify GPU is detected
- [ ] Check CUDA version matches requirements
- [ ] Verify at least 4GB VRAM available

## Core Functionality Testing

### 1. Audio Capture Testing
```bash
python tests/test_audio_minimal.py
```
- [ ] Audio devices list correctly
- [ ] Microphone is detected
- [ ] Audio levels show activity when speaking
- [ ] No permission errors
- [ ] 5-second capture completes without errors

### 2. Keyboard Injection Testing
```bash
python tests/test_keyboard_output.py
```
- [ ] Test 1: Direct output works
- [ ] Test 2: Threaded output works
- [ ] Test 3: Callback mechanism works
- [ ] Text appears in target application
- [ ] No permission errors
- [ ] Focus handling works correctly

### 3. Windows Injection Strategies
```bash
python tests/test_windows_injection_debug.py
```
- [ ] Menu appears correctly
- [ ] Test each injection method:
  - [ ] UI Automation (Option 1)
  - [ ] Keyboard Library (Option 2)
  - [ ] Clipboard (Option 3)
  - [ ] SendInput (Option 4)
- [ ] Test with different applications:
  - [ ] Notepad
  - [ ] Web Browser
  - [ ] VS Code
  - [ ] Terminal/CMD
- [ ] Special characters test (Option 5)
- [ ] Performance benchmark runs (Option 6)

### 4. LocalAgreement Testing
```bash
python tests/test_local_agreement.py
```
- [ ] Agreement buffer logic works
- [ ] Text commits after threshold
- [ ] Pending text displays correctly
- [ ] No text rewrites occur

### 5. Full System Testing
```bash
python -m personalparakeet
```
- [ ] System starts without errors
- [ ] F4 hotkey toggles dictation
- [ ] Visual feedback shows status
- [ ] Speech is captured when speaking
- [ ] Text appears with proper timing
- [ ] No jarring rewrites (LocalAgreement working)
- [ ] System stops cleanly with Ctrl+C

## Application-Specific Testing

### Test in Each Application
- [ ] **Notepad**: Basic text appears correctly
- [ ] **VS Code**: Code dictation works, indentation preserved
- [ ] **Chrome/Edge**: Web forms accept input
- [ ] **Microsoft Word**: Formatted text works
- [ ] **Terminal/PowerShell**: Commands can be dictated

### Edge Cases
- [ ] Long sentences (30+ words)
- [ ] Numbers and punctuation
- [ ] Mixed case words
- [ ] Technical terms
- [ ] Silence periods (no phantom text)
- [ ] Background noise handling

## Performance Testing

### Resource Usage
- [ ] GPU usage stays under 90%
- [ ] Memory usage under 4GB
- [ ] No memory leaks over time
- [ ] CPU usage reasonable

### Latency Testing
- [ ] Speech to text: < 700ms
- [ ] F4 hotkey response: < 50ms
- [ ] No audio dropouts
- [ ] Smooth real-time performance

## Error Recovery Testing

### Failure Scenarios
- [ ] Microphone disconnection
- [ ] GPU out of memory
- [ ] Application loses focus
- [ ] Network issues (for model download)
- [ ] Invalid audio device selection

### Recovery Validation
- [ ] Error messages are clear
- [ ] System recovers gracefully
- [ ] Fallback mechanisms work
- [ ] No crashes or hangs

## Configuration Testing

### Device Selection
```bash
python -m personalparakeet --list-devices
python -m personalparakeet --device 2
python -m personalparakeet --device-name "Blue Yeti"
```
- [ ] Device listing works
- [ ] Specific device selection works
- [ ] Invalid device handling

### Configuration Profiles
- [ ] Default (Balanced) mode works
- [ ] Can switch between profiles
- [ ] Custom configuration loads

## Regression Testing

### After Code Changes
- [ ] All unit tests pass: `python tests/run_all_tests.py`
- [ ] Core functionality still works
- [ ] No new warnings/errors
- [ ] Performance unchanged

## Sign-off Checklist

### Ready for Use
- [ ] All core tests pass
- [ ] No critical errors
- [ ] Performance acceptable
- [ ] Documentation updated
- [ ] Known issues documented

### Test Report
- [ ] Date tested: ___________
- [ ] Tester: ___________
- [ ] Windows version: ___________
- [ ] GPU model: ___________
- [ ] Issues found: ___________

## Quick Test Command Sequence

For rapid validation, run these in order:
```bash
# 1. Basic audio test
python tests/test_audio_minimal.py

# 2. Keyboard output test  
python tests/test_keyboard_output.py

# 3. Full injection test
python tests/test_windows_injection_debug.py

# 4. Run main system
python -m personalparakeet
```

## Notes

- Always test with a real microphone
- Run as Administrator on Windows
- Close other audio applications
- Test in a quiet environment initially
- Keep GPU monitoring open (`nvidia-smi -l 1`)