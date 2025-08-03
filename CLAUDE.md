# PersonalParakeet - Claude Code Context

PersonalParakeet v3: Real-time dictation system with transparent floating UI.

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
conda activate personalparakeet
poetry install
poetry run personalparakeet
# or
python -m personalparakeet
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

## Documentation
- [QUICKSTART.md](docs/QUICKSTART.md) - Setup guide
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Design decisions
- [DEVELOPMENT.md](docs/DEVELOPMENT.md) - Full reference
- [STATUS.md](docs/STATUS.md) - Progress tracking

**Remember**: Simpler is better. One process, one language, one executable.