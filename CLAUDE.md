# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PersonalParakeet is a real-time dictation system using NVIDIA Parakeet-TDT 0.6B v2 model. The project focuses on implementing a "LocalAgreement buffering" system that prevents text rewrites and provides a superior dictation experience.

### Current Branch Structure
- `main`: Clean reset approach with single-file implementation  
- `community-wrapper`: FastAPI wrapper approach (current branch)

## Essential Commands

### FastAPI Service (parakeet-fastapi-wrapper)
```bash
# Install dependencies
pip install -r parakeet-fastapi-wrapper/requirements.txt

# Run development server
cd parakeet-fastapi-wrapper
uvicorn parakeet_service.main:app --host 0.0.0.0 --port 8000

# Docker deployment
docker build -t parakeet-stt .
docker run -d -p 8000:8000 --gpus all parakeet-stt

# Docker Compose
docker-compose up --build
```

### Testing and Development
```bash
# Test Windows audio capture (critical for main dictation system)
python test_audio_minimal.py

# GPU monitoring
nvidia-smi
watch -n 1 nvidia-smi

# Manual testing only (DO NOT run automatically)
pytest test_components.py
```

## Architecture Overview

### FastAPI Service Architecture
The `parakeet-fastapi-wrapper/` contains a production-ready STT service:

- **REST API**: `POST /transcribe` for file uploads with OpenAI-compatible interface
- **WebSocket Streaming**: Real-time transcription at `ws://localhost:8000/ws`
- **Core Components**:
  - `main.py`: FastAPI app initialization and lifecycle
  - `routes.py`: REST endpoints implementation  
  - `stream_routes.py`: WebSocket streaming handler
  - `model.py`: Parakeet ASR model interface
  - `audio.py`: Audio preprocessing utilities
  - `batchworker.py`: Micro-batch processing for GPU efficiency
  - `streaming_vad.py`: Voice activity detection using Silero VAD
  - `chunker.py`: Audio segmentation
  - `config.py`: Environment-based configuration

### Main Project Architecture
The root level contains essential implementation files for the core dictation system:

- **ESSENTIAL_LocalAgreement_Code.py**: Complete LocalAgreement buffer implementation (318 lines) - the core differentiator that prevents text rewrites
- **ESSENTIAL_RTX_Config.py**: Dual RTX 5090/3090 GPU optimization (228 lines)
- **ESSENTIAL_Audio_Integration.py**: Basic audio capture and WebSocket server (264 lines)
- **test_audio_minimal.py**: Windows audio debugging script (currently working)

## Key Configuration

### Environment Variables (FastAPI Service)
```bash
MODEL_PRECISION=fp16      # Model precision (fp16/fp32)
DEVICE=cuda              # Computation device
BATCH_SIZE=4             # Processing batch size
TARGET_SR=16000          # Target sample rate
MAX_AUDIO_DURATION=30    # Max audio length in seconds
VAD_THRESHOLD=0.5        # Voice activity threshold
LOG_LEVEL=INFO           # Logging verbosity
PROCESSING_TIMEOUT=60    # Processing timeout in seconds
```

## Critical Development Notes

### Current Status (July 2025)
- **Working**: Parakeet transcription, FastAPI service, GPU utilization
- **Broken**: Windows audio capture (blocking issue), LocalAgreement buffering not implemented
- **Priority**: Focus on single-file implementations until basic functionality works

### Development Constraints
- **Windows compatibility required** - primary target platform
- **Single-file approach preferred** - avoid complex package structures until basics work
- **LocalAgreement buffering is the core differentiator** - must be implemented
- **Avoid scope creep** - see SCOPE_CREEP_LESSONS.md for lessons learned

### FastAPI Service Endpoints
- Health check: `GET /healthz`
- Transcription: `POST /transcribe` (multipart audio upload)
- WebSocket streaming: `ws://localhost:8000/ws` (16kHz mono PCM)
- API documentation: `http://localhost:8000/docs`

## Implementation Roadmap Reference

Follow `IMPLEMENTATION_ROADMAP.md` for 21-day focused development plan. Essential files are ready for immediate integration:
- Copy ESSENTIAL_LocalAgreement_Code.py → algorithms/local_agreement.py
- Copy ESSENTIAL_RTX_Config.py → gpu/manager.py  
- Copy ESSENTIAL_Audio_Integration.py → audio/capture.py

## Testing Notes

- Audio capture testing via `test_audio_minimal.py` is critical for Windows compatibility
- Manual testing preferred over automated testing until basic functionality is stable
- GPU monitoring essential during development due to dual RTX setup
- Test on Windows immediately - every change must work on target platform