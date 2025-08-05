# PersonalParakeet Project Overview

## Purpose
PersonalParakeet v3 is a real-time dictation system with:
- Transparent floating UI built with Flet
- AI-powered corrections using "Clarity Engine"
- LocalAgreement buffering system to prevent text rewrites
- GPU-accelerated speech recognition using NVIDIA Parakeet
- Cross-platform text injection with multiple strategies

## Target Accuracy
- 6.05% Word Error Rate (WER) target
- <150ms latency requirement

## Architecture
- **Single-process Python architecture** (v3 rewrite)
- **NO WebSocket/IPC/subprocess for UI** - uses Flet directly
- Producer-consumer pattern with queue.Queue
- asyncio.run_coroutine_threadsafe() for thread-safe UI updates
- Dataclass-based configuration system

## Key Innovation
**LocalAgreement Buffering**: Core innovation that prevents jarring text rewrites by only committing text that is stable across multiple transcription updates.

## System Requirements
- Python 3.11+
- NVIDIA GPU (recommended) or CPU mode
- 8GB RAM minimum
- Real hardware required (no mock tests)

## Project Status
- 20% complete (realistic assessment)
- Focus on end-to-end integration testing
- Hardware-based testing only (no mocks allowed)