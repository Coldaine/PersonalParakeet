# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# PersonalParakeet - Claude Code Context

PersonalParakeet v3: Real-time dictation system with transparent floating UI.

## ⚠️ CRITICAL REQUIREMENT FOR ALL AGENTS ⚠️
**ALWAYS run `conda activate personalparakeet` before ANY other command!**
This project uses conda environment management and will fail without proper activation.

## Hardware Requirements
- **Physical hardware ALWAYS present** - No mock tests allowed/required
- Real microphone, GPU, and audio hardware available at all times
- All STT testing uses actual speech recognition models
- No mock/stub implementations needed for hardware components

## Current Status
- **Architecture**: Single-process Python using Flet (no WebSocket/IPC)
- **Progress**: 20% complete (realistic assessment)
- **Focus**: End-to-end integration testing

## Key Commands
```bash
# CRITICAL: Environment setup - ALWAYS activate conda first!
# ⚠️  ALL AGENTS MUST RUN THIS COMMAND BEFORE ANY OTHER COMMANDS ⚠️
conda activate personalparakeet

# Install dependencies
poetry install

# IMPORTANT: Install PyTorch nightly for RTX 5090
poetry run pip install -r requirements-torch.txt

# Run application (after conda activate!)
poetry run personalparakeet
# or
python -m personalparakeet

# Run tests (after conda activate!)
poetry run pytest
poetry run pytest tests/integration/test_full_pipeline.py  # Specific test

# Code quality (after conda activate!)
poetry run black . --line-length 100
poetry run isort . --profile black
poetry run ruff check .
poetry run mypy .
```

## Dependency Resolution Process

### ⚠️ CRITICAL: PyTorch Version Compatibility Fix ⚠️

If you encounter the following dependency errors:
- `RuntimeError: operator torchvision::nms does not exist`
- Version conflicts between torch, torchvision, and torchaudio
- fsspec version conflicts with NeMo

Use this exact sequence to fix:

```bash
# PREREQUISITE: Always activate conda environment first
conda activate personalparakeet

# Step 1: Fix TorchVision (downgrade from dev to stable)
poetry run pip uninstall -y torchvision
poetry run pip install torchvision==0.22.0 --index-url https://download.pytorch.org/whl/cu128

# Step 2: Fix fsspec for NeMo compatibility
poetry run pip install fsspec==2024.12.0

# Step 3: Fix TorchAudio (downgrade from dev to stable)
poetry run pip uninstall -y torchaudio
poetry run pip install torchaudio==2.7.0 --index-url https://download.pytorch.org/whl/cu128

# Step 4: Verify all imports work
poetry run python -c "import torch; import torchvision; import torchaudio; print('✅ All PyTorch packages imported successfully')"
poetry run python -c "import nemo.collections.asr as nemo_asr; print('✅ NeMo imported successfully')"

# Step 5: Test the application
poetry run python -m personalparakeet
```

### Why These Specific Versions?

- **PyTorch 2.7.0**: Stable version with CUDA 12.8 support for RTX 5090
- **TorchVision 0.22.0**: Matches PyTorch 2.7.0, avoids nms operator issues
- **TorchAudio 2.7.0**: Matches PyTorch 2.7.0, maintains compatibility
- **fsspec 2024.12.0**: Exact version required by NeMo 2.4.0

### Alternative: Clean Install

If issues persist, use the provided script:
```bash
./fix_ml_dependencies.sh
```

## Architecture Constraints

### ❌ FORBIDDEN
- WebSocket servers/clients
- subprocess for UI
- Multi-process architecture
- Cross-thread UI access
- Tauri/React/Node.js

### ✅ REQUIRED
- Producer-consumer with queue.Queue
- asyncio.run_coroutine_threadsafe() for UI
- Dataclass configuration
- Direct function calls

## Project Structure
```
src/
└── personalparakeet/
    ├── __main__.py         # Entry point
    ├── main.py            # Application bootstrap
    ├── config.py          # Dataclass configuration
    ├── core/              # Business logic (STT, VAD, etc)
    │   ├── stt_processor.py
    │   ├── stt_factory.py
    │   ├── clarity_engine.py
    │   └── text_injector.py
    └── ui/                # Flet UI components
        └── dictation_view.py
tests/
├── hardware/              # Hardware validation tests
├── integration/           # End-to-end tests
└── unit/                 # Unit tests
```

## Threading Model
```python
# Audio Producer (sounddevice callback)
def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

# STT Consumer (background thread)
def stt_worker(page):
    while True:
        chunk = audio_queue.get()
        text = model.transcribe(chunk)
        # Thread-safe UI update
        asyncio.run_coroutine_threadsafe(
            update_ui(text), page.loop
        )
```

## Core Features
- **LocalAgreement Buffering**: Prevents text rewrites by only committing stable text
- **High-Performance STT**: GPU-accelerated using NVIDIA Parakeet (6.05% WER target)
- **Floating UI**: Transparent, draggable window above other applications
- **Clarity Engine**: Real-time homophone and technical jargon corrections
- **Smart Text Injection**: Multi-strategy, platform-aware text input
- **Advanced VAD**: Dual VAD system (Silero + WebRTC)
- **Configuration Profiles**: Runtime-switchable presets (Fast/Balanced/Accurate)

## Testing Strategy
- All tests use real hardware (microphone, GPU, audio)
- Integration tests verify end-to-end functionality
- Hardware validation ensures environment readiness
- Performance benchmarks track <150ms latency requirement

## Documentation
- [QUICKSTART.md](docs/QUICKSTART.md) - Setup guide
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Design decisions
- [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Full reference
- [STATUS.md](docs/STATUS.md) - Progress tracking

**Remember**: Simpler is better. One process, one language, one executable.