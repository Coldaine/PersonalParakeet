# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PersonalParakeet is a real-time dictation system featuring the **Dictation View** - a transparent, floating UI that provides live transcription feedback with real-time AI text corrections. The system uses NVIDIA Parakeet-TDT 1.1B model with direct NeMo integration.

### Current Status (July 2025)
- **v2 (Tauri/WebSocket)**: Current but deprecated - has critical architectural issues
- **v3 (Rust+EGUI)**: In active development - single-process Python backend with Rust UI via PyO3

**IMPORTANT**: All new development should focus on the v3 Rust+EGUI refactor. See:
- [Implementation Plan](docs/Rust_EGUI_Implementation_Plan.md)
- [Architecture Decision Record](docs/Architecture_Decision_Record_Rust_EGUI.md)
- [**Feature Migration Status**](@docs/V3_FEATURE_MIGRATION_STATUS.md) - Comprehensive v2→v3 feature porting tracker

## v3 Rust+EGUI Architecture (NEW)

### Key Decisions Made
1. **UI Framework**: Rust EGUI with PyO3 bridge to Python backend
2. **Process Model**: Single Python process with Rust UI (no IPC/WebSocket)
3. **Threading**: Producer-consumer pattern with crossbeam channels
4. **Deployment**: Maturin build system for Rust-Python integration
5. **State Management**: EGUI reactive UI with Python backend state

### Development Focus
```bash
# New v3 structure
personal-parakeet-rust-egui/
├── main.py                 # Python entry point with Rust UI integration
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
1. **Week 1**: Core Rust EGUI app + audio pipeline
2. **Week 2**: Port all v2 features to Rust+EGUI
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

### For v3 Development (Rust+EGUI)
```bash
# Setup
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install maturin sounddevice numpy torch nemo_toolkit

# Run
python main.py

# Build Rust extension
maturin develop
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

### Rust+EGUI UI Pattern
```python
# Python side
gui_controller = personalparakeet_ui.GuiController()
gui_controller.update_text(text, "APPEND_WITH_SPACE")
gui_controller.run()

# Rust side (src/gui.rs)
impl eframe::App for GuiApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        // EGUI immediate mode UI updates
    }
}
```

## Migration Notes

When migrating v2 code to v3:
1. **Remove all WebSocket code**
2. **Replace React components with EGUI widgets**
3. **Use PyO3 bridge for Python-Rust communication**
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
