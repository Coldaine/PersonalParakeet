# GitHub Copilot Instructions for PersonalParakeet

## Model Preference
**Preferred Model**: Claude 3.5 Sonnet (or newer Sonnet 4 when available)
- This project benefits from Claude's strong Python analysis and architectural understanding
- Claude excels at understanding complex threading patterns and UI frameworks

## Project Context

PersonalParakeet is a real-time dictation system undergoing a critical v2→v3 migration:
- **Current State**: 35% complete migration from Tauri/WebSocket (v2) to Flet (v3)
- **Architecture**: Single-process Python with producer-consumer threading
- **Core Tech**: NVIDIA Parakeet-TDT 1.1B, Flet UI, PyTorch, NeMo Toolkit

## Critical Migration Context

**IMPORTANT**: We are migrating FROM a broken two-process architecture TO a simpler single-process design:
- **v2 (DEPRECATED)**: Tauri + React frontend, Python WebSocket backend - DO NOT USE
- **v3 (ACTIVE)**: Pure Python with Flet UI framework - ALL NEW WORK HERE

See @docs/V3_FEATURE_MIGRATION_STATUS.md for the complete migration roadmap.

## Code Review Priorities

When reviewing PRs and commits, focus on:

### 1. Architecture Compliance
- ❌ REJECT any WebSocket, IPC, or multi-process patterns
- ✅ ENSURE single-process design with threading
- ✅ VERIFY Flet reactive patterns (no manual DOM manipulation)
- ✅ CHECK producer-consumer pattern for audio processing

### 2. Threading Safety
```python
# GOOD: Thread-safe pattern
audio_queue = queue.Queue()
asyncio.run_coroutine_threadsafe(update_ui(text), page.loop)

# BAD: Direct cross-thread access
self.ui_element.value = text  # Will cause race conditions
```

### 3. Migration Tracking
- Verify features match v2→v3 migration matrix in @docs/V3_FEATURE_MIGRATION_STATUS.md
- Check that deprecated v2 code isn't being reintroduced
- Ensure new features follow v3 patterns in @docs/V3_PROVEN_CODE_LIBRARY.md

### 4. Performance Requirements
- End-to-end latency must be <150ms
- Memory usage should stay under 4GB
- GPU utilization should be monitored (targeting RTX 5090 optimization)

## Code Style Guidelines

### Python Patterns
- Use dataclasses for all configuration
- Type hints required for all functions
- Async/await for UI updates only
- Follow existing patterns in `v3-flet/` directory

### File Organization
```
v3-flet/
├── core/           # Business logic (STT, VAD, Clarity)
├── ui/             # Flet components only
├── main.py         # Entry point
└── config.py       # Dataclass configuration
```

### Import Style
```python
# Standard library
import asyncio
from dataclasses import dataclass

# Third-party
import flet as ft
import numpy as np

# Local - always use relative imports in v3
from .core import stt_processor
from .ui import components
```

## Issue Assignment Guidelines

When working on PersonalParakeet issues:

### High Priority (Week 2 Focus)
1. **Enhanced Application Detection** - Port from `personalparakeet/application_detection_enhanced.py`
2. **Multi-Strategy Text Injection** - Complete injection system with fallbacks
3. **Configuration Profiles** - Runtime switching without restart

### Implementation Notes
- Always check @CLAUDE.md for architecture decisions
- Reference @docs/KNOWLEDGE_BASE.md for proven patterns
- Test with real microphone input (no mock audio)
- Verify on both Windows and Linux when possible

## Common Pitfalls to Avoid

1. **DO NOT** use subprocess to launch UI components
2. **DO NOT** create new WebSocket servers or clients  
3. **DO NOT** split functionality across multiple processes
4. **DO NOT** use React, Tauri, or web technologies
5. **DO NOT** ignore the 6-week migration roadmap

## Testing Requirements

All PRs must:
- Run `python v3-flet/run_tests.py` successfully
- Test with actual audio input (not mocked)
- Verify <150ms latency requirement
- Include updates to migration tracking if porting v2 features

## Natural Language Preferences

- Be concise but thorough in PR descriptions
- Explain the "why" not just the "what" in commits
- Reference specific files with line numbers when discussing code
- Use the migration matrix terminology from V3_FEATURE_MIGRATION_STATUS.md

## Security Considerations

- Never commit audio recordings or transcription logs
- Ensure GPU memory is properly released
- Validate all user configuration inputs
- Keep dependencies minimal (see v3-flet/requirements-v3.txt)

---

**Remember**: Simpler is better. One process, one language, one executable.

When in doubt, check:
1. @docs/V3_FEATURE_MIGRATION_STATUS.md - Current progress
2. @docs/V3_PROVEN_CODE_LIBRARY.md - Battle-tested patterns
3. @CLAUDE.md - Architecture decisions