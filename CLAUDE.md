# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PersonalParakeet is a real-time dictation system featuring the **Dictation View** - a transparent, floating UI that provides live transcription feedback with real-time AI text corrections. The system uses NVIDIA Parakeet-TDT 1.1B model with direct NeMo integration.

### Current Status (July 2025)
- **v2 (Tauri/WebSocket)**: Current but deprecated - has critical architectural issues
- **v3 (Flet)**: In active development - single-process Python solution

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

### Development Focus
```bash
# New v3 structure
personal-parakeet-flet/
├── main.py                 # Flet app entry point
├── audio_engine.py         # Producer-consumer audio
├── ui/
│   ├── dictation_view.py   # Main UI component
│   └── components.py       # Reusable elements
├── core/
│   ├── stt_processor.py    # Parakeet integration
│   ├── clarity_engine.py   # Port from v2
│   └── vad_engine.py       # Port from v2
└── requirements.txt        # Simplified deps
```

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

### For v3 Development (Flet)
```bash
# Setup
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install flet sounddevice numpy torch nemo_toolkit

# Run
python main.py

# Package
pyinstaller --onefile --windowed main.py
```

### For v2 Maintenance Only
```bash
# DO NOT use for new development
python start_dictation_view.py  # Broken due to npm issues
python start_integrated.py      # Attempted fix
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

## Migration Notes

When migrating v2 code to v3:
1. **Remove all WebSocket code**
2. **Replace React components with Flet widgets**
3. **Use Flet's event system instead of WebSocket messages**
4. **Preserve core logic from:
   - clarity_engine.py
   - vad_engine.py  
   - dictation.py (Parakeet integration)

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

## Current Work

Focus on Phase 1 of the implementation plan:
1. Create basic Flet window
2. Implement audio producer-consumer
3. Display mock transcriptions
4. Test threading patterns

Remember: **Simpler is better**. One process, one language, one executable.