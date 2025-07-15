# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PersonalParakeet is a real-time dictation system using NVIDIA Parakeet-TDT 1.1B model with direct NeMo integration. The project has successfully implemented a "LocalAgreement buffering" system that prevents text rewrites and provides a superior dictation experience.

### Current Branch Structure
- `main`: Clean reset approach with single-file implementation  
- `community-wrapper`: Working direct NeMo integration (current branch)

## Essential Commands

### Direct NeMo Integration (Working System)
```bash
# Install dependencies
pip install sounddevice numpy nemo-toolkit torch keyboard

# Run complete working dictation system
python updated-project/dictation_simple_fixed.py

# Test core components individually
python test_audio_minimal.py                    # Windows audio capture
python updated-project/test_local_agreement.py  # LocalAgreement logic
python updated-project/test_keyboard_output.py  # Keyboard output
```

### Development and Testing
```bash
# Test Windows audio capture (critical for system functionality)
python test_audio_minimal.py

# GPU monitoring (essential for performance)
nvidia-smi
watch -n 1 nvidia-smi

# Test LocalAgreement buffer system (core innovation)
python updated-project/test_local_agreement.py

# Manual testing only (DO NOT run automatically)
# System requires interactive testing with real microphone input
```

## Architecture Overview

### Direct NeMo Integration Architecture
The system uses direct integration with NVIDIA NeMo framework for real-time dictation:

- **Single-file deployment** - Simple, maintainable architecture
- **Direct model loading** - No API wrapper overhead
- **Real-time processing** - Chunk-based audio processing with GPU acceleration
- **LocalAgreement buffering** - Core innovation preventing text rewrites

### Core Implementation Files
The project contains proven working implementations:

- **`updated-project/dictation_simple_fixed.py`**: Complete working system (203 lines) - **CURRENTLY WORKING**
- **`ESSENTIAL_LocalAgreement_Code.py`**: LocalAgreement buffer implementation (318 lines) - core differentiator
- **`ESSENTIAL_RTX_Config.py`**: Dual RTX 5090/3090 GPU optimization (228 lines)
- **`ESSENTIAL_Audio_Integration.py`**: Audio capture and processing (264 lines)
- **`test_audio_minimal.py`**: Windows audio debugging script (**WORKING**)

## Key Configuration

### System Configuration
```bash
# Core dependencies
pip install sounddevice numpy nemo-toolkit torch keyboard

# Hardware requirements
NVIDIA GPU (RTX 3090/5090 recommended)
Windows 10/11 (primary target)
CUDA 12.1+ compatible drivers

# Audio settings
SAMPLE_RATE=16000        # Target sample rate for Parakeet
CHUNK_DURATION=1.0       # Audio chunk size in seconds
AUDIO_CHANNELS=1         # Mono audio processing
```

## Critical Development Notes

### Current Status (July 2025)
- **Working**: Complete end-to-end dictation system, LocalAgreement buffering, Windows audio capture
- **Working**: Parakeet transcription, GPU acceleration, real-time processing, hotkey integration
- **Minor Issues**: Text output callback refinement needed, error handling enhancement
- **Priority**: Polish working system, fix minor text output issues

### Development Constraints
- **Windows compatibility required** - primary target platform
- **Single-file approach preferred** - proven working architecture
- **LocalAgreement buffering is the core differentiator** - **IMPLEMENTED AND WORKING**
- **Avoid scope creep** - see SCOPE_CREEP_LESSONS.md for lessons learned

### Working System Features
- **F4 hotkey toggle** - Start/stop dictation functionality
- **Real-time processing** - 2-3 iterations per second, responsive performance
- **LocalAgreement buffering** - Text stabilization preventing rewrites
- **Universal output** - Works with any Windows application
- **GPU acceleration** - Optimized for RTX hardware

## Implementation Status

The core system is **WORKING** with proven functionality:
- **`updated-project/dictation_simple_fixed.py`**: Complete working dictation system
- **`ESSENTIAL_LocalAgreement_Code.py`**: Core LocalAgreement implementation (ready for integration)
- **`ESSENTIAL_RTX_Config.py`**: GPU optimization strategies (ready for integration)
- **`ESSENTIAL_Audio_Integration.py`**: Audio pipeline foundation (ready for integration)

## Testing Notes

- **`test_audio_minimal.py` is WORKING** - Windows audio compatibility confirmed
- **Manual testing preferred** - System requires interactive testing with real microphone input
- **GPU monitoring essential** - Use `nvidia-smi` and `watch -n 1 nvidia-smi` for performance monitoring
- **Test on Windows immediately** - Every change must work on target platform
- **Component testing available** - Individual test scripts for LocalAgreement, keyboard output, etc.