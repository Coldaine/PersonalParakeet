# Workshop Box Troubleshooting & Restart Guide

## Current Issue: GUI Not Appearing

The Workshop Box backend is running but the Tauri GUI is not appearing due to Rust/Cargo not being in the system PATH.

## Immediate Problem

**Error**: `Error failed to get cargo metadata: program not found`

**Root Cause**: Rust/Cargo is installed at `C:\Users\pmacl\.cargo\bin\` but not in system PATH

## Required Steps After Shell Restart

### 1. Fix Rust PATH Issue
```bash
# Add Cargo to PATH permanently
setx PATH "%PATH%;%USERPROFILE%\.cargo\bin"
```

**Then restart your terminal/command prompt**

### 2. Verify Dependencies
```bash
# Check Rust is available
rustc --version
cargo --version

# Check Node.js
node --version
npm --version

# Activate virtual environment
.venv\Scripts\activate

# Verify PyTorch RTX 5090 support
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"
```

### 3. Start Workshop Box
```bash
# Method 1: Use the start script (recommended)
python start_workshop_box.py

# Method 2: Manual start (for debugging)
# Terminal 1: Start backend
python workshop_websocket_bridge_v2.py

# Terminal 2: Start UI
cd workshop-box-ui
npm run tauri dev
```

## What Should Happen

1. **Backend**: Python WebSocket server starts on ws://127.0.0.1:8765
2. **Model Loading**: Parakeet-TDT-1.1B loads with RTX 5090 acceleration
3. **Tauri Compilation**: First run takes 1-2 minutes to compile Rust
4. **GUI Appears**: Transparent glass morphism window appears
5. **Connection**: Green indicator shows backend connection

## Expected Output

Backend startup:
```
2025-07-19 05:11:32,268 - websockets.server - INFO - server listening on 127.0.0.1:8765
2025-07-19 05:11:32,268 - __main__ - INFO - WebSocket server started on ws://127.0.0.1:8765
2025-07-19 05:11:32,268 - __main__ - INFO - Workshop Box ready - speak into your microphone!
```

## Current Status

✅ **Working Components:**
- PyTorch 2.9.0.dev20250716+cu128 with RTX 5090 support
- Audio capture (43 devices detected)
- NeMo toolkit and Parakeet model
- WebSocket backend functionality
- Virtual environment with dependencies

❌ **Issue:**
- Rust/Cargo not in PATH preventing Tauri GUI startup

## Next Steps After PATH Fix

1. Kill any hanging Python processes: `taskkill /f /im python.exe`
2. Add Rust to PATH and restart terminal
3. Run `python start_workshop_box.py`
4. Wait for Tauri compilation (1-2 minutes first run)
5. Look for transparent Workshop Box window

## Troubleshooting Commands

```bash
# Check running processes
tasklist | findstr python
tasklist | findstr node

# Kill processes if needed
taskkill /f /im python.exe
taskkill /f /im node.exe

# Test individual components
python test_audio_flow.py

# Check WebSocket manually
# (requires websockets: pip install websockets)
python -c "import asyncio; import websockets; asyncio.run(websockets.connect('ws://localhost:8765'))"
```

## File Structure Check

Ensure these files exist:
- `start_workshop_box.py` - Main launcher
- `workshop_websocket_bridge_v2.py` - Backend server
- `workshop-box-ui/` - Tauri frontend directory
- `.venv/` - Virtual environment with dependencies
- `test_audio_flow.py` - Component testing script