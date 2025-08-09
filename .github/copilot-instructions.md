---
description: "PersonalParakeet v3 migration guidelines and architecture requirements"
applyTo: "**"
---

# PersonalParakeet Copilot Instructions

## Critical Project Context

PersonalParakeet is a real-time dictation system using NVIDIA Parakeet-TDT 1.1B. We are at 35% completion of a critical v2→v3 migration:

- **v2 (DEPRECATED)**: Tauri + React frontend, Python WebSocket backend - DO NOT USE
- **v3 (ACTIVE)**: Python backend with Rust+EGUI UI via PyO3 bridge - ALL NEW WORK HERE

## Architecture Requirements

### Single-Process Design (MANDATORY)
- ❌ REJECT any WebSocket, IPC, or multi-process patterns
- ❌ REJECT subprocess calls for UI components
- ✅ REQUIRE single Python process with threading
- ✅ REQUIRE producer-consumer pattern with queue.Queue

### Threading Pattern
```python
# CORRECT: Thread-safe communication
audio_queue = queue.Queue()
asyncio.run_coroutine_threadsafe(update_ui(text), page.loop)

# WRONG: Direct cross-thread access
self.ui_element.value = text  # Race condition
```

## Code Review Priorities

1. **Architecture Compliance**: Verify single-process design
2. **Migration Status**: Check against @docs/V3_FEATURE_MIGRATION_STATUS.md
3. **Threading Safety**: Ensure proper queue usage
4. **Performance**: <150ms latency requirement

## Development Guidelines

### Current Week 2 Focus
- Enhanced Application Detection (port from v2)
- Multi-Strategy Text Injection
- Configuration Profiles (runtime switching)

### File Structure
```
src/personalparakeet/
├── core/           # Business logic only
├── ui/             # Python UI bridge to Rust+EGUI
├── main.py         # Single entry point
└── config.py       # Dataclass configuration
```

### Code Style
- Dataclasses for all configuration
- Type hints required
- Async/await for UI updates only
- Follow patterns in @docs/V3_PROVEN_CODE_LIBRARY.md

## Testing Requirements
- Test with real microphone input
- Verify <150ms latency
- Run: `poetry run pytest tests/`

## References
- @docs/STATUS.md - Migration roadmap (50% complete)
- @docs/ARCHITECTURE.md - Battle-tested patterns
- @CLAUDE.md - Architecture decisions and history
