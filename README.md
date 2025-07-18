# PersonalParakeet - Real-Time Dictation System

PersonalParakeet is a real-time dictation system using NVIDIA Parakeet-TDT model with direct NeMo integration. The project's core innovation is the **LocalAgreement buffering system** that prevents jarring text rewrites and provides a superior dictation experience.

## 🎉 BREAKTHROUGH: Core System is Working!

The project has successfully implemented a complete end-to-end dictation system with:

- **✅ Windows audio capture** - Real-time microphone input with proper levels
- **✅ Parakeet transcription** - NVIDIA model processing speech to text in real-time  
- **✅ LocalAgreement buffering** - Text stabilization with committed vs pending logic
- **✅ Real-time processing** - 2-3 iterations per second, responsive performance
- **✅ Hotkey integration** - F4 toggle functionality operational

## Architecture Overview

### Direct NeMo Integration
The system uses direct integration with NVIDIA NeMo framework:
- **Parakeet-TDT-1.1B model** - Direct model loading and inference
- **Single-file deployment** - Simple, maintainable architecture
- **GPU acceleration** - CUDA 12.1 compatible with RTX 5090/3090 optimization

### Core Components

#### Core Implementation Files
- **`personalparakeet/dictation.py`** - Main dictation system with complete integration
- **`personalparakeet/local_agreement.py`** - LocalAgreement buffer implementation (core differentiator)
- **`personalparakeet/cuda_fix.py`** - RTX 5090 CUDA compatibility fix
- **`run_dictation.py`** - Ready-to-use entry point for the complete system

#### LocalAgreement Innovation
The core differentiator that prevents text rewrites:
```
🔊 Processing audio chunk (level: 0.386)
🎯 Raw transcription: 'well'
✅ Committed: '' | ⏳ Pending: 'well'

🔊 Processing audio chunk (level: 0.475)  
🎯 Raw transcription: 'oh shit this is actually'
✅ Committed: '' | ⏳ Pending: 'oh shit this is actually'

🔊 Processing audio chunk (level: 0.353)
🎯 Raw transcription: 'fucking working'
✅ Committed: 'well' | ⏳ Pending: 'working'
```

## Quick Start

### Dependencies
```bash
pip install sounddevice numpy nemo-toolkit torch keyboard
```

### Basic Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Test audio capture (critical first step)
python tests/test_audio_minimal.py

# Run the dictation system
python -m personalparakeet

# Or install as package and run
pip install -e .
personalparakeet

# Test LocalAgreement logic
python tests/test_local_agreement.py
```

### Hardware Requirements
- **Windows 10/11** - Primary target platform
- **NVIDIA GPU** - RTX 3090/5090 recommended with CUDA 12.1+
- **Microphone** - Any Windows-compatible audio input device

## Key Features

### 1. LocalAgreement Buffering
- **Committed vs Pending Text** - Prevents jarring rewrites
- **Agreement Threshold** - Configurable stability requirements
- **Position Tolerance** - Handles transcription variations gracefully
- **Timeout Handling** - Automatic commit of stale pending text

### 2. Real-Time Processing
- **Chunk-based Audio** - 1-second audio chunks for responsiveness
- **GPU Acceleration** - Optimized for RTX hardware
- **Voice Activity Detection** - Intelligent silence handling
- **Multi-threaded** - Separate audio capture and processing threads

### 3. System Integration
- **F4 Hotkey Toggle** - Start/stop dictation
- **Universal Text Output** - Works with any Windows application
- **Real-time Feedback** - Visual processing status and debugging

## Current Status

### Working Components ✅
- Windows audio capture via sounddevice
- Parakeet transcription with NeMo integration
- LocalAgreement buffer system (core innovation)
- Real-time processing pipeline
- Hotkey integration and system controls

### System Status ✅
- **Complete working system** - All core functionality implemented and stable
- **LocalAgreement buffering** - Core innovation preventing text rewrites
- **Real-time performance** - Responsive dictation with GPU acceleration
- **Windows compatibility** - Fully functional on target platform

## Development Guidelines

### Implementation Constraints
- **Single-file approach** - Keep implementations simple until proven
- **Windows compatibility** - All features must work on target platform
- **Direct testing** - Manual verification preferred over automated testing
- **LocalAgreement first** - Core differentiator takes priority

### Testing Strategy
```bash
# Audio hardware testing
python tests/test_audio_minimal.py

# LocalAgreement algorithm testing  
python tests/test_local_agreement.py

# Keyboard output testing
python tests/test_keyboard_output.py

# End-to-end system testing
python -m personalparakeet
```

## Project Structure

```
PersonalParakeet/
├── personalparakeet/           # Main package
│   ├── __init__.py
│   ├── dictation.py           # Main dictation system
│   ├── local_agreement.py     # LocalAgreement buffering
│   └── cuda_fix.py            # RTX 5090 CUDA compatibility
├── tests/                     # Test suite
│   ├── test_audio_minimal.py  # Windows audio test (✅ Working!)
│   ├── test_local_agreement.py
│   └── test_keyboard_output.py
├── docs/                      # Documentation
│   ├── SCOPE_CREEP_LESSONS.md # Development lessons learned
│   ├── LLM_REFINEMENT_EXAMPLES.md
│   └── GUI_FEATURE_PLANNING.md # Future GUI feature planning
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── CLAUDE.md                # Claude Code assistant guidance
```

## Next Steps

1. **Enhancement opportunities** - Polish user interface and feedback
2. **Performance optimization** - Further improve processing efficiency  
3. **Advanced features** - Add voice commands and controls
4. **User experience** - Refine interface and visual feedback
5. **Deployment** - Package for easy distribution

The core breakthrough is complete - PersonalParakeet successfully demonstrates superior dictation experience through LocalAgreement buffering with a **fully functional working system**!
