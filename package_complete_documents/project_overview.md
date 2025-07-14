# Parakeet Dictation Project Overview

## Purpose
Advanced dictation system using NVIDIA Parakeet model for real-time speech-to-text with GPU acceleration, dual VAD, LLM refinement, and smart text injection.

## Tech Stack
- **Language**: Python 3.x
- **ML Framework**: PyTorch with CUDA support
- **Transcription Model**: NVIDIA Parakeet TDT 0.6B v2
- **LLM**: Ollama (llama2:7b default)
- **Audio**: sounddevice, webrtcvad, silero-vad
- **System Integration**: pynput, pygetwindow, pyperclip, win32gui (Windows)
- **GPU**: Dual GPU setup (Parakeet on GPU 0, Ollama on GPU 1)

## Key Features
1. Dual VAD (Silero + WebRTC) for accurate speech detection
2. Streaming transcription with context and stability tracking
3. Smart text injection based on active application
4. LLM refinement with context awareness
5. Real-time statistics overlay
6. Multiple hotkeys (F4: Toggle, F5: LLM, F6: Overlay, Ctrl+Alt+Q: Quit)

## Architecture
- **audio_handler.py**: 16kHz audio capture with dual VAD processing
- **transcriber.py**: Streaming Parakeet with 3-second buffer and context
- **text_output.py**: Smart injection (paste for editors, type for browsers)
- **llm_refiner.py**: Context-aware refinement on secondary GPU
- **dictation.py**: Main application orchestrating all components