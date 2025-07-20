# PersonalParakeet Project Overview

## Purpose
PersonalParakeet is a real-time dictation system using NVIDIA Parakeet-TDT 1.1B model with direct NeMo integration. The core innovation is the **LocalAgreement buffering system** that prevents jarring text rewrites and provides a superior dictation experience.

## Current Status
- **WORKING SYSTEM**: Complete end-to-end dictation functionality implemented
- **Core Innovation**: LocalAgreement buffering prevents text rewrites
- **Platform**: Windows 10/11 primary target, Linux support available
- **Architecture**: Single-file deployment with direct NeMo integration

## Key Components
- **Main Entry**: `run_dictation.py` - Ready-to-use entry point
- **Core System**: `personalparakeet/dictation.py` - Complete working dictation system
- **Innovation**: `personalparakeet/local_agreement.py` - LocalAgreement buffer implementation
- **GPU Support**: `personalparakeet/cuda_fix.py` - RTX 5090 CUDA compatibility

## Tech Stack
- **Python**: 3.11+ (specified in pyproject.toml)
- **AI Framework**: NVIDIA NeMo toolkit with Parakeet-TDT model
- **Audio**: sounddevice library for real-time capture
- **System Integration**: keyboard library for hotkeys, Windows text injection
- **GPU**: CUDA 12.1+ for RTX hardware acceleration