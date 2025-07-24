# Workshop Box Crash Fixes

## Summary of Issues Found and Fixed

### 1. **Undefined Variable in dictation.py**
- **Issue**: Line 513 referenced `hotkey_config.toggle_dictation` but `hotkey_config` was not defined
- **Fix**: Changed to use `keyboard.remove_all_hotkeys()` instead
- **Location**: `personalparakeet/dictation.py:513`

### 2. **Wrong Method Names in WebSocket Bridge**
- **Issue**: WebSocket bridge was calling `start_recording()` and `stop_recording()` methods
- **Fix**: Changed to correct method names `start_dictation()` and `stop_dictation()`
- **Location**: `workshop_websocket_bridge_v2.py:214,221`

### 3. **Missing Constructor Parameters**
- **Issue**: SimpleDictation constructor signature changed but WebSocket bridge wasn't updated
- **Fix**: Added missing `audio_input_callback` and `stt_callback` parameters (set to None)
- **Location**: `workshop_websocket_bridge_v2.py:61-67`

### 4. **Missing Rust Dependency**
- **Issue**: `futures_util` import in main.rs but not in Cargo.toml
- **Fix**: Added `futures-util = "0.3"` to dependencies
- **Location**: `workshop-box-ui/src-tauri/Cargo.toml`

## How to Test the Fixes

1. **Run the test script**:
   ```bash
   python test_websocket_fixes.py
   ```

2. **Start the WebSocket bridge**:
   ```bash
   python workshop_websocket_bridge_v2.py
   ```

3. **Build and run the Tauri app** (from workshop-box-ui directory):
   ```bash
   npm install
   npm run tauri dev
   ```

## Additional Recommendations

1. **Error Handling**: The dictation system should handle model loading failures more gracefully
2. **Logging**: Consider adding more detailed logging for debugging WebSocket communication
3. **Configuration**: Consider making the WebSocket port configurable
4. **Reconnection**: The Tauri app has good reconnection logic, but Python side could benefit from similar robustness

## Common Runtime Issues to Watch For

1. **CUDA/GPU Issues**: Ensure NVIDIA drivers are installed and CUDA is available
2. **Audio Device Issues**: The system will prompt for device selection if default fails
3. **Model Loading**: Parakeet model download can take time on first run
4. **Port Conflicts**: Ensure port 8765 is not in use by another application

## Quick Troubleshooting

If crashes persist:

1. Check Python console for error messages
2. Check Tauri console (DevTools) for JavaScript errors
3. Verify all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   npm install  # in workshop-box-ui directory
   ```
4. Try running components separately to isolate issues
5. Check Windows Event Viewer or system logs for crash details