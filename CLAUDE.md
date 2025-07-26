# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PersonalParakeet is a real-time dictation system featuring the **Dictation View** - a transparent, floating UI that provides live transcription feedback with real-time AI text corrections. The system uses NVIDIA Parakeet-TDT 1.1B model with direct NeMo integration.

### Current Status (July 26, 2025)
- **v2 (Tauri/WebSocket)**: Deprecated - has critical architectural issues
- **v3 (Flet)**: In active development - single-process Python solution

**REALITY CHECK**: Previous 35% completion estimate was overly optimistic and based on file count rather than working functionality.

**IMPORTANT**: All new development should focus on the v3 Flet refactor. See:
- [Implementation Plan](docs/Flet_Refactor_Implementation_Plan.md)
- [Architecture Decision Record](docs/Architecture_Decision_Record_Flet.md)
- [**Feature Migration Status**](@docs/V3_FEATURE_MIGRATION_STATUS.md) - Comprehensive v2→v3 feature porting tracker

## v3 Flet Architecture (NEW)

### Key Decisions Made
1. **UI Framework**: Flet (Python-native, Material Design)
2. **Process Model**: Single Python process (no IPC/WebSocket)
3. **Threading**: Producer-consumer pattern with queue.Queue
4. **Deployment**: PyInstaller single executable
5. **State Management**: Flet reactive components

### Development Focus - v3 Structure (ACTUAL)
```bash
# Current v3 structure (as-built)
v3-flet/
├── main.py                      # Flet app entry point 🚧
├── audio_engine.py              # Producer-consumer audio 🚧
├── config.py                    # Dataclass configuration 🚧
├── ui/
│   ├── dictation_view.py        # Main UI component 🚧
│   ├── components.py            # Reusable elements ✅
│   └── theme.py                 # Material design theme ✅
├── core/
│   ├── stt_processor.py         # MOCK ONLY - no real NeMo ⭕
│   ├── clarity_engine.py        # Text corrections ✅
│   ├── vad_engine.py            # Voice activity detection ✅
│   ├── injection_manager.py     # Basic text injection 🚧
│   └── thought_linker.py        # Placeholder ⭕
├── tests/                       # v3 test suite 🚧
├── requirements-v3.txt          # Python-only deps ✅
└── README.md                    # v3 architecture docs ✅
```

**File Status Legend**: ✅ Working | 🚧 In Progress | ⭕ Placeholder | ❌ Missing

**CRITICAL**: Most components are incomplete or mocked. No proven end-to-end functionality.

### Implementation Priorities
1. **Week 1**: Core Flet app + audio pipeline
2. **Week 2**: Port all v2 features to Flet
3. **Week 3**: Polish and advanced features  
4. **Week 4**: PyInstaller packaging

## v2 Architecture (DEPRECATED)

The v2 system uses a problematic two-process architecture:
- **Frontend**: Tauri (Rust) + React
- **Backend**: Python WebSocket server
- **Issues**: Race conditions, complex deployment, shell conflicts

### Why v2 Failed
1. **Process synchronization** - WebSocket race conditions
2. **Deployment complexity** - Requires Node.js, Rust, Python
3. **Path/shell issues** - npm using Git Bash causing failures
4. **User feedback** - "Process management nightmare"

## Essential Commands

### For v3 Development (Flet) - ACTIVE DEVELOPMENT
```bash
# Setup v3 environment with Poetry (RECOMMENDED)
cd v3-flet/
poetry install
poetry install --with ml  # For real STT (NeMo/PyTorch)
poetry shell

# Alternative: Manual venv setup (if Poetry not available)
python -m venv .venv
source .venv/bin/activate  # Linux/WSL
# OR: .venv\Scripts\activate  # Windows
pip install -r requirements-v3.txt

# Check ML stack (NEW)
python ml_stack_check.py

# Run v3 app
poetry run python main.py
# OR: python main.py  (if in poetry shell or venv)

# Run v3 tests
poetry run python run_tests.py
poetry run python test_injection.py  # Test text injection specifically
poetry run python test_stt_integration.py  # Test STT integration

# Package v3 (when mature)
poetry run pyinstaller --onefile --windowed main.py
```

**STT Configuration**: 
- Default: Real STT (requires ML deps)
- Testing: Set `"use_mock_stt": true` in config.json

**IMPORTANT**: Never use `--break-system-packages`. Use Poetry or virtual environments to avoid breaking system Python.

### For v2 (DEPRECATED - DO NOT USE)
```bash
# v2 commands are broken - DO NOT USE for new development
python start_dictation_view.py  # Broken due to npm/Tauri issues
```

### Testing Commands
```bash
# Run comprehensive test suite
python tests/run_all_tests.py

# Test specific components
pytest tests/unit/         # Unit tests
pytest tests/integration/  # Integration tests (may require hardware)
pytest -m "not hardware"   # Skip hardware-dependent tests

# v3-specific testing
cd v3-flet/
python -m pytest tests/    # v3 component tests
```

### Development Tools
```bash
# Code formatting
black personalparakeet/ v3-flet/ --line-length 100
isort personalparakeet/ v3-flet/ --profile black

# Type checking
mypy personalparakeet/ --ignore-missing-imports

# Linting
flake8 personalparakeet/ v3-flet/
```

## Core Features to Preserve

All v2 features must be ported to v3:

1. **Dictation View UI**
   - Transparent, floating window
   - Real-time transcription display
   - Draggable positioning
   - Status indicators

2. **Clarity Engine**
   - Real-time text corrections
   - Technical term recognition
   - Homophone fixes
   - Already working in v2

3. **Voice Activity Detection**
   - Pause detection (1.5s default)
   - Auto-commit functionality
   - Visual indicators

4. **Advanced Features**
   - Command Mode activation
   - Intelligent Thought-Linking
   - Session management

## Technical Guidelines

### Threading Pattern (v3)
```python
# Producer (audio callback)
def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

# Consumer (STT worker)
def stt_worker(page):
    while True:
        chunk = audio_queue.get()
        text = model.transcribe(chunk)
        # Thread-safe UI update
        asyncio.run_coroutine_threadsafe(
            update_ui(text), page.loop
        )
```

### Flet UI Pattern
```python
class DictationView:
    def __init__(self, page):
        self.page = page
        self.transcript = ft.Text("")
        
    async def update_transcript(self, text):
        self.transcript.value = text
        await self.page.update_async()
```

## Key v2 Source Files for Migration

**Critical v2 modules to port to v3** (located in `personalparakeet/`):

### ✅ Already Ported
- `clarity_engine.py` → `v3-flet/core/clarity_engine.py`
- `vad_engine.py` → `v3-flet/core/vad_engine.py`  
- `dictation.py` → `v3-flet/core/stt_processor.py`
- `basic_injection.py` → `v3-flet/core/injection_manager.py` (basic only)

### 🚧 Currently Being Ported (Week 2 Priority)
- `application_detection_enhanced.py` → `v3-flet/core/application_detector.py`
- `text_injection_enhanced.py` → enhance existing `injection_manager.py`
- `config_manager.py` → enhance existing `v3-flet/config.py`

### ❌ Not Yet Started (Weeks 3-4)
- `command_mode.py` → `v3-flet/core/command_processor.py`
- `thought_linking.py` → `v3-flet/core/thought_linker.py`
- `audio_devices.py` → `v3-flet/core/audio_manager.py`
- `dictation_enhanced.py` → `v3-flet/core/enhanced_dictation.py`

### Platform-Specific (Week 5)
- `windows_injection.py`, `linux_injection.py`, `kde_injection.py`
- `windows_clipboard_manager.py`, `linux_clipboard_manager.py`

## Migration Guidelines

When migrating v2 code to v3:
1. **Remove all WebSocket code** - No more `websockets` imports or async WebSocket handlers
2. **Replace subprocess calls** - Direct function calls instead of process communication
3. **Use Flet's event system** - `page.update_async()` instead of WebSocket messages
4. **Preserve core business logic** - The algorithms work, just change the integration layer
5. **Use dataclass configuration** - Replace dict-based config with type-safe dataclasses

## Testing Requirements

1. **Audio capture** - Test with real microphone
2. **GPU performance** - Monitor with nvidia-smi
3. **UI responsiveness** - Ensure <100ms updates
4. **Packaging** - Test PyInstaller output on clean system

## Success Criteria

v3 must achieve:
- Single-click launch
- No process errors
- <2 second startup
- All v2 features working
- <100MB executable

## Current Work (July 26, 2025 - Reality Check)

**ACTUAL Migration Progress**: 15-20% Complete (Functional System)
**Previous Estimate**: 35% was based on file count, not working functionality

### Realistic Progress Assessment:
- **Foundation**: 60% complete (Flet UI structure, basic architecture)
- **Core Features**: 25% complete (some components ported but not integrated)
- **Advanced Features**: 5% complete (mostly placeholders)
- **Overall Functional System**: **15-20% complete**

### What Actually Works ✅:
- Clarity Engine (fully ported from v2)
- VAD Engine (fully ported from v2)
- Basic Flet UI components and theme
- Enhanced Injection Manager (recently added, needs verification)

### Recently Completed ✅ (July 26, 2025):
- **Real STT Integration** - NeMo/PyTorch integration with smart fallback
- **STT Factory Pattern** - Dynamic loading with error handling
- **CUDA Compatibility** - RTX 5090 detection and fixes
- **ML Dependencies** - Poetry optional group configuration

### Still Missing/Incomplete ❌:
- **Audio Pipeline** - basic structure but needs end-to-end testing
- **Application Detection** - file exists but functionality unverified
- **End-to-End Testing** - no proven full pipeline functionality

**Current Phase**: Foundation building - need working STT integration before claiming higher completion

See [V3_FEATURE_MIGRATION_STATUS.md](docs/V3_FEATURE_MIGRATION_STATUS.md) for detailed progress tracking.

## Architecture Constraints (CRITICAL)

**❌ FORBIDDEN PATTERNS** - These will break the v3 architecture:
- WebSocket servers or clients
- subprocess calls for UI components  
- Multi-process architecture
- Direct cross-thread UI access
- Any Tauri/React/Node.js dependencies

**✅ REQUIRED PATTERNS** - Single-process Flet architecture:
- Producer-consumer with `queue.Queue`
- `asyncio.run_coroutine_threadsafe()` for UI updates
- Dataclass-based configuration
- Direct function calls between components

Remember: **Simpler is better**. One process, one language, one executable.