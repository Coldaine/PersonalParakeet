# v2 Development Commands for PersonalParakeet

## Quick Start Commands (v2 Dictation View System)
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install UI dependencies  
cd dictation-view-ui && npm install && cd ..

# Start complete Dictation View system
python start_dictation_view.py

# Or run components separately:
python dictation_websocket_bridge.py     # Backend WebSocket server
cd dictation-view-ui && npm run tauri dev # Frontend UI
```

## Virtual Environment Setup (Optional)
```bash
# Current status: No .venv exists, system Python 3.13.5 in use
# Project expects Python 3.11+ (per .python-version)

# Option 1: Use current system Python 3.13.5
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Option 2: Use Python 3.11 (matches project specification)
"C:\Program Files\Python311\python.exe" -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Core Testing Commands
```bash
# Test audio capture (critical for system functionality)
python tests/test_audio_minimal.py

# Test Clarity Engine corrections
python test_clarity_engine_integration.py

# Test WebSocket communication
python test_websocket_fixes.py

# GPU monitoring (essential for performance)
nvidia-smi
```

## Frontend Development (Tauri/React)
```bash
# Navigate to UI directory
cd dictation-view-ui

# Install dependencies
npm install

# Development mode (hot reload)
npm run tauri dev

# Build for production
npm run tauri build

# Type checking
npm run type-check

# Return to project root
cd ..
```

## Backend Development
```bash
# Run WebSocket server independently
python dictation_websocket_bridge.py

# Test individual components
python personalparakeet/dictation.py      # STT testing
python personalparakeet/clarity_engine.py # Text corrections
python personalparakeet/vad_engine.py     # Voice activity detection

# Configuration management
python personalparakeet/config_manager.py
```

## Integration Testing
```bash
# Complete system test (manual verification required)
python start_dictation_view.py

# Audio flow testing
python test_audio_flow.py

# Command mode testing (if implemented)
python test_command_mode_simulation.py
```

## Development Tools
```bash
# Code formatting (if dev dependencies installed)
black --line-length 100 .
isort --profile black .

# Type checking
mypy personalparakeet/

# Audio device listing
python -c "import sounddevice; print(sounddevice.query_devices())"

# CUDA availability check
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

## Project Status Monitoring
```bash
# Check current configuration
python config_tool.py

# Run comprehensive tests
python run_all_tests.py

# Check for required dependencies
python -c "import torch, sounddevice, websockets; print('Core deps OK')"
```

## Windows-Specific Commands
```powershell
# Check Python versions available
where python
python --version

# PowerShell directory listing
Get-ChildItem -Force

# Continuous GPU monitoring
while($true) { nvidia-smi; Start-Sleep 1; Clear-Host }
```

## Important Notes
- **Manual testing required**: Dictation View needs real microphone input testing
- **GPU monitoring essential**: Use `nvidia-smi` for performance monitoring
- **v2 Architecture**: Always use `start_dictation_view.py` as main entry point
- **WebSocket Communication**: Backend must be running for UI to function properly