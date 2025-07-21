# PersonalParakeet v2 Dictation View Setup Guide

## Overview

PersonalParakeet v2 introduces the **Dictation View** - a transparent, always-visible UI that displays real-time transcription as you speak. This provides a modern glass-morphism interface with real-time feedback and text corrections.

## Prerequisites

### Required Software

1. **Python 3.11.9** (exact version for compatibility)
   - Download from: https://www.python.org/downloads/release/python-3119/

2. **Node.js** (v16 or later)
   - Download from: https://nodejs.org/

3. **Rust** (for Tauri framework)
   - Download from: https://www.rust-lang.org/tools/install
   - Run installer and follow prompts

4. **Microsoft C++ Build Tools** (Windows only)
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - During installation, select "Desktop development with C++"

### Hardware Requirements

- **NVIDIA GPU** with CUDA support (RTX 3090/4090/5090 recommended)
- **CUDA 12.1+** compatible drivers
- **4GB+ GPU memory** for Parakeet-TDT-1.1B model
- **Microphone** for audio input

## Installation Steps

### 1. Clone and Setup Python Environment

```bash
# Clone the repository
git clone https://github.com/YourRepo/PersonalParakeet.git
cd PersonalParakeet

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Install Tauri UI Dependencies

```bash
# Navigate to UI directory
cd workshop-box-ui

# Install Node dependencies
npm install

# Return to main directory
cd ..
```

### 3. Verify Installation

```bash
# Check Rust installation
rustc --version
cargo --version

# Check Node installation
node --version
npm --version

# Check CUDA availability
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Running Workshop Box

### Quick Start (Windows)

Simply double-click or run:
```bash
python start_workshop_simple.py
```

This will:
1. Start the Python WebSocket backend with Parakeet STT
2. Launch the Tauri Workshop Box UI
3. Begin listening to your microphone automatically

### Manual Start (Advanced)

If you prefer to run components separately:

**Terminal 1 - Python Backend:**
```bash
.venv\Scripts\python workshop_websocket_bridge_v2.py
```

**Terminal 2 - Tauri UI:**
```bash
cd workshop-box-ui
npm run tauri dev
```

## First Run

On first run, Tauri will compile the Rust backend, which takes 1-2 minutes. You'll see:
- Compilation progress in the terminal
- After compilation, the Workshop Box window will appear
- Look for the status indicator (green = connected, red = disconnected)

## Using Workshop Box

### UI Features

- **Transparent Window**: Glass-morphism design with blur effects
- **Draggable**: Click and drag anywhere on the window to move it
- **Always-on-Top**: Stays visible above other windows
- **Adaptive Sizing**: Automatically adjusts size based on text length
  - Compact: 1-10 words
  - Standard: 10-50 words  
  - Extended: 50+ words

### Status Indicators

- **Green dot (pulsing)**: Connected and listening
- **Blue dot (pulsing)**: Actively transcribing speech
- **Red dot (pulsing)**: Disconnected from backend

### Controls

- **F4**: Toggle dictation on/off (when implemented)
- **Escape**: Hide Workshop Box
- **Drag window**: Move to desired position

## Troubleshooting

### "Rust not found" Error
```bash
# Install Rust from https://rustup.rs/
# Restart terminal after installation
```

### "Cannot find module" Errors
```bash
# Ensure you're in the correct directory
cd workshop-box-ui
npm install
```

### GPU/CUDA Errors
```bash
# For RTX 5090 or CUDA issues:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

### Workshop Box Not Appearing
1. Check both console windows for errors
2. Ensure Python backend shows "Dictation started automatically"
3. Look for "Connected to Python backend!" in Tauri console
4. Try moving mouse to different screen areas (in case window is off-screen)

### Audio Not Working
1. Check default microphone in system settings
2. Ensure no other apps are using microphone
3. Look for "Audio callback status" warnings in Python console

## Configuration

### Audio Settings
Edit `personalparakeet/config.py` or create `.env` file:
```env
SAMPLE_RATE=16000
CHUNK_DURATION=0.5
AUDIO_DEVICE_INDEX=0
```

### UI Themes
The Workshop Box supports multiple themes (edit in code):
- Dark (default)
- Light
- High Contrast

### Window Position
Window position is not currently persisted between sessions. Drag to preferred location after startup.

## Architecture

```
┌─────────────────────────┐
│   Workshop Box UI       │
│  (Tauri + React)       │
│                         │
│  • Glass morphism      │
│  • Adaptive sizing     │
│  • Real-time display   │
└───────────┬─────────────┘
            │ WebSocket (ws://localhost:8765)
┌───────────▼─────────────┐
│   Python Backend        │
│  (PersonalParakeet)     │
│                         │
│  • Parakeet STT        │
│  • Audio capture       │
│  • CUDA acceleration   │
└─────────────────────────┘
```

## Development

### Building for Production

```bash
# Build optimized Tauri app
cd workshop-box-ui
npm run tauri build

# Output will be in src-tauri/target/release/
```

### Debugging

- **Enable DevTools**: Press F12 in Workshop Box window
- **Check WebSocket**: Open browser to http://localhost:8765
- **Python Logs**: See console output from `workshop_websocket_bridge_v2.py`
- **Tauri Logs**: Check second console window

## Future Features (Planned)

- **Clarity Engine**: LLM-powered real-time corrections
- **Command Mode**: Voice commands with "Parakeet Command" trigger
- **Intelligent Thought-Linking**: Context-aware paragraph detection
- **Configuration UI**: Settings panel for audio/display options

## Support

For issues or questions:
1. Check console output for error messages
2. Ensure all prerequisites are installed
3. Try the manual start method for better error visibility
4. Create an issue with full error logs

---

**Note**: This is the v2 "Workshop Model" implementation. For the older LocalAgreement buffering system, see the v1 documentation.