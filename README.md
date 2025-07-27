# PersonalParakeet 🦜

> 🚀 **v3.0-alpha Available!** PersonalParakeet has been completely rewritten with a modern single-process architecture.
> - **v2 (Deprecated)** - Tauri/WebSocket version with architectural issues
> - **v3 (Active)** - Flet-based solution with enhanced features - [See Current Status](v3-flet/docs/CURRENT_V3_STATUS.md)
> 
> For the architectural decisions, see [Architecture Decision Record](docs/Architecture_Decision_Record_Flet.md).

PersonalParakeet is a real-time dictation system powered by NVIDIA's Parakeet-TDT 1.1B model, featuring the **Dictation View** - a transparent, floating UI that provides live transcription with AI-powered text corrections.

## 🎯 Core Innovation: The Dictation View

The Dictation View is a semi-transparent, always-on-top UI element that serves as a "scratchpad" for live transcription:

- **Real-time feedback** - See STT output and corrections as they happen
- **Clarity Engine** - Built-in LLM corrections for homophones and technical jargon  
- **Glass morphism UI** - Beautiful transparent interface with blur effects
- **Adaptive sizing** - Grows/shrinks based on content length
- **Commit & Control** - Explicit user control over text finalization

## 🚀 Quick Start (v3)

### Prerequisites
- **Python 3.11+**
- **NVIDIA GPU** (recommended) or CPU-only mode
- **CUDA 11.8+** for GPU acceleration
- **Poetry** (recommended) or pip

### Installation
```bash
# Clone repository
git clone <repository>
cd PersonalParakeet/v3-flet

# Install with Poetry (recommended)
poetry install
poetry install --with ml  # For real STT

# Or with pip
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements-v3.txt
```

### Usage
```bash
# Check ML dependencies
python ml_stack_check.py

# Run the application
poetry run python main.py
# Or with venv: python main.py
```

### Configuration
- For testing without GPU: Set `"use_mock_stt": true` in config.json
- See [ML Installation Guide](v3-flet/docs/ML_INSTALLATION_GUIDE.md) for GPU setup

## ✨ Key Features

### 1. Dictation View UI
- **Transparent interface** - Glass morphism with blur effects
- **Draggable positioning** - Move anywhere on screen
- **Adaptive sizing** - 3-state breathing system (Compact/Standard/Extended)
- **Connection status** - Visual indicator (green=connected, red=disconnected)
- **Always-on-top** - Stays visible over all applications

### 2. Clarity Engine Integration
Real-time text corrections powered by rule-based engine:
- `clod code` → `claude code`
- `cloud code` → `claude code` 
- `get hub` → `github`
- `pie torch` → `pytorch`
- `dock her` → `docker`
- `colonel` → `kernel`
- Plus homophone corrections (`too/to`, `your/you're`, etc.)

### 3. Voice Activity Detection
- **Automatic commit** - Natural pause detection triggers text injection
- **Configurable thresholds** - Customize silence and pause detection
- **Visual feedback** - VAD status shown in UI

### 4. Commit & Control Logic
Three distinct actions for text finalization:
- **Commit & Continue** - Sustained pause (>1.5s) injects text and continues
- **Commit & Execute** - Enter key injects text + Enter press
- **Abort & Clear** - Escape key discards all text

## 🏗️ Architecture

### Backend (Python)
- **`workshop_websocket_bridge.py`** - Main WebSocket server
- **`personalparakeet/dictation.py`** - Parakeet-TDT integration  
- **`personalparakeet/clarity_engine.py`** - Real-time text corrections
- **`personalparakeet/vad_engine.py`** - Voice activity detection

### Frontend (Tauri/React)
- **`workshop-box-ui/`** - Tauri application with React components
- **WebSocket communication** - Real-time updates from backend
- **Modern UI** - TypeScript + Zustand state management

### Platform Support
- **Windows**: Primary supported platform.
- **Linux**: Initial support for KDE Wayland environments.

### Key Components
```
PersonalParakeet v2/
├── workshop_websocket_bridge.py     # Main backend server
├── start_workshop_box.py            # Unified launcher
├── personalparakeet/                # Core package
│   ├── dictation.py                 # Parakeet integration
│   ├── clarity_engine.py            # Text corrections  
│   ├── vad_engine.py                # Voice activity detection
│   └── config_manager.py            # Configuration system
├── workshop-box-ui/                 # Tauri frontend
│   ├── src/components/WorkshopBox.tsx
│   ├── src/stores/transcriptionStore.ts  
│   └── src-tauri/                   # Rust backend
└── docs/                            # Documentation
```

## 🔧 Configuration

Configuration via `config.json`:
```json
{
  "audio_device_index": null,
  "sample_rate": 16000,
  "vad": {
    "custom_threshold": 0.01,
    "pause_duration_ms": 1500
  },
  "clarity": {
    "enabled": true
  }
}
```

## 🎮 Controls

- **F4** - Toggle dictation on/off (planned)
- **Drag** - Move Dictation View position
- **Escape** - Abort current transcription
- **Enter** - Commit text with execute action
- **Natural pause** - Auto-commit after 1.5 seconds

## 📊 Current Status

### ✅ Working Features
- Dictation View UI with glass morphism effects
- Real-time transcription display  
- Clarity Engine text corrections
- WebSocket communication
- Voice activity detection
- Basic commit & control logic

### 🚧 In Development  
- Command Mode ("Parakeet Command" activation)
- Intelligent Thought-Linking
- Enhanced pause detection
- Session management

### 🎯 Next Steps
1. Implement Command Mode voice activation
2. Add Intelligent Thought-Linking for multi-sentence composition
3. Polish UI animations and effects
4. Add comprehensive testing suite

## 💡 Innovation

PersonalParakeet v2 represents a paradigm shift in dictation UX. Instead of hiding the "messiness" of real-time STT behind complex algorithms, we expose it in a beautiful, controlled interface that gives users transparency and control while delivering perfectly clean results to their applications.

The Dictation View turns the inherent uncertainty of real-time speech recognition into a feature, not a bug.