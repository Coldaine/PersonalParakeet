# PersonalParakeet v2 Project Overview

## Purpose
PersonalParakeet v2 is a real-time dictation system featuring the **Dictation View** - a transparent, floating UI that provides live transcription feedback with real-time AI text corrections. The system uses NVIDIA Parakeet-TDT 1.1B model with direct NeMo integration.

## Current Status: Actively Developed v2 System
- **WORKING**: Dictation View UI with glass morphism effects
- **WORKING**: WebSocket communication between frontend and backend
- **WORKING**: Clarity Engine real-time text corrections (ultra-fast rule-based)
- **WORKING**: Voice activity detection with pause triggers
- **IN PROGRESS**: Command Mode and Intelligent Thought-Linking

## Architecture Overview
### Modern Client-Server Design
- **Backend (Python)**: WebSocket server with Parakeet integration
- **Frontend (Tauri/React)**: Modern UI with transparent effects
- **Real-time Communication**: WebSocket for live transcription updates
- **Clarity Engine**: Built-in text corrections for better accuracy

## Key Components
- **`start_dictation_view.py`**: Main entry point - launches complete system
- **`dictation_websocket_bridge.py`**: WebSocket server and backend logic (MAIN BACKEND)
- **`dictation-view-ui/`**: Tauri frontend with React components
- **`personalparakeet/dictation.py`**: Parakeet-TDT integration for STT
- **`personalparakeet/clarity_engine.py`**: Real-time text corrections (WORKING)
- **`personalparakeet/vad_engine.py`**: Voice activity detection
- **`personalparakeet/config_manager.py`**: Configuration management

## Technology Stack
- **Python**: 3.11+ (per .python-version file)
- **AI Framework**: NVIDIA NeMo toolkit with Parakeet-TDT model
- **Frontend**: Tauri + React + TypeScript + Vite
- **Communication**: WebSocket protocol for real-time updates
- **Audio**: sounddevice library for real-time capture
- **GPU**: CUDA 12.1+ for RTX hardware acceleration
- **Platform**: Windows 10/11 primary, designed for cross-platform expansion

## Core Features (Working)
- **Dictation View UI**: Transparent, draggable, adaptive sizing interface
- **Real-time Transcription**: Live feedback in beautiful interface
- **Clarity Engine**: Built-in corrections for technical terms and homophones
- **Voice Activity Detection**: Automatic commit on sustained pause
- **WebSocket Architecture**: Reliable real-time communication

## Development Focus
- **v2 Dictation View Priority**: All development centers on modern UI approach
- **Cross-platform Potential**: Tauri enables Linux/macOS expansion
- **GPU Performance**: NVIDIA CUDA drivers essential for Parakeet
- **Modern Web Tech**: React/TypeScript for maintainable UI development