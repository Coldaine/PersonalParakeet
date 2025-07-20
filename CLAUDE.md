# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PersonalParakeet v2 is a real-time dictation system featuring the **Dictation View** - a transparent, floating UI that provides live transcription feedback with real-time AI text corrections. The system uses NVIDIA Parakeet-TDT 1.1B model with direct NeMo integration.

## Essential Commands

### Dictation View System (v2)
```bash
# Install dependencies
pip install -r requirements.txt

# Install UI dependencies  
cd dictation-view-ui && npm install && cd ..

# Start complete Dictation View system
python start_dictation_view.py

# Or run components separately:
python dictation_websocket_bridge.py     # Backend WebSocket server
cd dictation-view-ui && npm run tauri dev # Frontend UI

# Test core components
python tests/test_audio_minimal.py      # Audio capture testing
python test_clarity_engine_integration.py  # Clarity Engine testing
```

### Development and Testing
```bash
# Test audio capture (critical for system functionality)
python tests/test_audio_minimal.py

# GPU monitoring (essential for performance)
nvidia-smi

# Test Clarity Engine corrections
python personalparakeet/clarity_engine.py

# Manual testing with real microphone input required
```

## Architecture Overview

### Dictation View v2 Architecture
The system uses a modern client-server architecture with WebSocket communication:

- **Backend (Python)** - WebSocket server with Parakeet integration
- **Frontend (Tauri/React)** - Modern UI with glass morphism effects  
- **Real-time communication** - WebSocket for live transcription updates
- **Clarity Engine** - Built-in text corrections for better accuracy

### Core Implementation Files
The project uses a clean modular architecture:

- **`start_dictation_view.py`**: Main entry point - launches complete system
- **`dictation_websocket_bridge.py`**: WebSocket server and backend logic - **MAIN BACKEND**
- **`personalparakeet/dictation.py`**: Parakeet-TDT integration for STT
- **`personalparakeet/clarity_engine.py`**: Real-time text corrections - **WORKING**
- **`personalparakeet/vad_engine.py`**: Voice activity detection
- **`personalparakeet/config_manager.py`**: Configuration management
- **`dictation-view-ui/`**: Tauri frontend with React components

## Key Configuration

### System Configuration
```bash
# Core dependencies (Python)
pip install sounddevice numpy nemo-toolkit torch

# UI dependencies (Node.js/Rust)
npm install  # In dictation-view-ui directory
cargo --version  # Rust required for Tauri

# Hardware requirements
NVIDIA GPU (RTX 3090/5090 recommended)
Windows 10/11 primary platform
CUDA 12.1+ compatible drivers
Node.js and Rust for UI compilation

# Configuration via config.json
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

## Critical Development Notes

### Current Status (July 2025)
- **Working**: Dictation View UI with glass morphism effects
- **Working**: WebSocket communication between frontend and backend
- **Working**: Clarity Engine real-time text corrections (ultra-fast rule-based)
- **Working**: Voice activity detection with pause triggers
- **In Progress**: Command Mode and Intelligent Thought-Linking

### Development Constraints
- **v2 Dictation View focus** - All development centers on Dictation View UI approach
- **Tauri/React frontend** - Modern web technologies for UI
- **WebSocket architecture** - Real-time communication between components
- **Clarity Engine priority** - Fast, accurate text corrections essential

### Working System Features
- **Dictation View UI** - Transparent, draggable, adaptive sizing
- **Real-time transcription** - Live feedback in beautiful interface
- **Clarity Engine** - Built-in corrections for technical terms and homophones
- **Voice activity detection** - Automatic commit on sustained pause
- **Cross-platform** - Windows primary, designed for expansion

## Implementation Status

The v2 system is **ACTIVELY DEVELOPED** with working components:
- **`dictation_websocket_bridge.py`**: Main backend server (integrated with Clarity Engine and VAD)
- **`personalparakeet/clarity_engine.py`**: Real-time text corrections (**WORKING**)
- **`dictation-view-ui/`**: Tauri frontend with React components
- **`start_dictation_view.py`**: Unified system launcher

## Cross-Platform Development Best Practices

### Environment Setup (Windows & Linux)
```bash
# Quick setup for new developers
python -m venv .venv

# Activation (platform-specific)
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies (same on all platforms)
pip install -r requirements.txt
```

### Git Workflow Best Practices  
```bash
# Safe branch switching (preserves .venv and node_modules)
git reset --hard
git pull origin main

# Emergency clean (removes everything except .gitignore items)
git clean -fdx  # Note: .venv and node_modules protected by .gitignore
```

### Virtual Environment Management
- **NEVER commit** virtual environments (.venv/, venv/) or node_modules/
- **Already protected** by .gitignore
- **Each developer** maintains their own environment
- **Fast recreation** using requirements.txt and package.json

### Dependency Management
```bash
# Python dependencies
pip freeze > requirements.txt

# UI dependencies  
cd workshop-box-ui && npm install

# Keep dependency files clean and minimal
```

### Platform-Specific Notes
- **Windows**: Primary platform with full Workshop Box support
- **Cross-platform potential**: Tauri enables Linux/macOS expansion
- **GPU requirements**: NVIDIA CUDA drivers essential for Parakeet
- **Audio systems**: sounddevice handles cross-platform audio capture
- **UI framework**: Tauri provides native performance with web technologies

## Testing Notes

- **`tests/test_audio_minimal.py`** - Cross-platform audio compatibility testing
- **Manual testing required** - Dictation View needs real microphone input testing
- **GPU monitoring essential** - Use `nvidia-smi` for performance monitoring
- **Component testing** - Individual test scripts for Clarity Engine, VAD, etc.
- **Frontend testing** - Tauri dev mode for UI development and testing