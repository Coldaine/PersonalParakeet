# PersonalParakeet Tech Stack

## Core Framework
- **UI**: Rust+EGUI (high-performance native UI via PyO3 bridge)
- **Architecture**: Single-process Python (no WebSocket/IPC)
- **Threading**: Producer-consumer with queue.Queue + asyncio

## Audio & STT Stack
- **Audio Capture**: sounddevice (primary), pyaudio (fallback)
- **Audio Processing**: numpy, scipy, soundfile
- **STT Engine**: NVIDIA Parakeet (GPU-accelerated)
- **VAD**: Dual system (Silero + WebRTC)

## ML Dependencies (Separate Management)
- **PyTorch**: 2.7.0 with CUDA 12.8 (RTX 5090 support)
- **TorchVision**: 0.22.0 (stable, matches PyTorch)
- **TorchAudio**: 2.7.0 (matches PyTorch)
- **NeMo**: 2.4.0 (NVIDIA toolkit)
- **fsspec**: 2024.12.0 (NeMo compatibility)

## System Integration
- **Input Injection**: pynput, keyboard
- **Clipboard**: pyperclip
- **Window Detection**: Cross-platform window detection
- **Configuration**: hydra-core, omegaconf, dataclasses-json

## Development Stack
- **Package Management**: Poetry + Conda hybrid
- **Environment**: Conda (personalparakeet env)
- **Python Version**: 3.11+ (ML compatibility)

## Dependency Management Strategy
- **Poetry**: Application dependencies (UI, audio, system)
- **requirements-torch.txt**: PyTorch with CUDA support
- **requirements-ml.txt**: NeMo and ML-specific packages
- **Separation Reason**: Complex version constraints and custom indices
