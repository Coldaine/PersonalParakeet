# PersonalParakeet - Claude Code Context

PersonalParakeet v3: Real-time dictation system with transparent floating UI.

## Current Status
- **Architecture**: Single-process Python using Flet (no WebSocket/IPC)
- **Progress**: 20% complete (realistic assessment)
- **Focus**: End-to-end integration testing

## Key Commands
```bash
cd v3-flet/
poetry install --with ml
poetry run python main.py
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