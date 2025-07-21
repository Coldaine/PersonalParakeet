# PersonalParakeet v2 → v3 Flet Code Reorganization Plan

## Executive Summary
This document provides explicit instructions for Gemini Flash to reorganize PersonalParakeet from the current v2 Tauri/WebSocket architecture to v3 Flet single-process architecture. Gemini should read all relevant v2 files and create a completely new v3 structure.

## Context for Gemini
You are helping reorganize PersonalParakeet, a real-time dictation system, from a problematic two-process architecture (Tauri + Python WebSocket) to a single-process Flet application. The core functionality (STT, text corrections, voice detection) works but the architecture is fundamentally flawed.

## Task Overview
1. **READ** all current v2 files to understand the codebase
2. **EXTRACT** reusable core logic (no UI, no WebSocket code)
3. **CREATE** new v3 file structure with Flet architecture
4. **PORT** relevant code with necessary adaptations
5. **GENERATE** new Flet UI components to replace React components

## New v3 Structure to Create

```
v3-flet/
├── main.py                    # NEW: Flet app entry point
├── audio_engine.py            # NEW: Producer-consumer audio pipeline
├── config.py                  # NEW: Dataclass-based config
├── requirements-v3.txt        # NEW: Simplified dependencies
├── ui/
│   ├── __init__.py
│   ├── dictation_view.py      # NEW: Main Flet UI component
│   ├── components.py          # NEW: Reusable Flet widgets  
│   └── theme.py               # NEW: Material Design theme
├── core/
│   ├── __init__.py
│   ├── stt_processor.py       # PORT: Extract from dictation.py
│   ├── clarity_engine.py      # PORT: Direct copy with minor updates
│   ├── vad_engine.py          # PORT: Direct copy with minor updates
│   └── thought_linker.py      # PORT: Extract any thought-linking logic
└── assets/
    └── icon.ico               # NEW: Placeholder app icon
```

## Files to Read and Analyze

### Core Logic Files (MUST READ)
- `personalparakeet/dictation.py` - Extract STT model loading and processing
- `personalparakeet/clarity_engine.py` - Port directly with minimal changes
- `personalparakeet/vad_engine.py` - Port directly, adapt callbacks
- `personalparakeet/config_manager.py` - Extract config logic, convert to dataclasses
- `dictation_websocket_bridge.py` - Extract main application flow logic

### UI Files (UNDERSTAND FUNCTIONALITY, DON'T PORT CODE)
- `dictation-view-ui/src/components/DictationView.tsx` - Understand UI requirements
- `dictation-view-ui/src/stores/transcriptionStore.ts` - Understand state management
- `dictation-view-ui/src/App.tsx` - Understand overall UI flow

### Configuration Files (REFERENCE)
- `config.json` - Understand current settings structure
- `requirements.txt` - See current dependencies

### Architecture Files (IGNORE - DON'T PORT)
- `start_dictation_view.py` - Process management (deprecated)
- `start_integrated.py` - WebSocket management (deprecated)
- All Tauri/React build files - Not needed in Flet

## Specific Porting Instructions

### 1. main.py - Create Flet Application Entry Point
```python
# Template structure - expand based on dictation_websocket_bridge.py logic
import flet as ft
import asyncio
import threading
from audio_engine import AudioEngine
from ui.dictation_view import DictationView

async def main(page: ft.Page):
    # Configure window for floating dictation view
    page.window_always_on_top = True
    page.window_frameless = True
    page.bgcolor = ft.colors.TRANSPARENT
    
    # Initialize components
    audio_engine = AudioEngine()
    dictation_view = DictationView(page, audio_engine)
    
    # Start audio processing
    audio_engine.start()
    
    # Add UI to page
    page.add(dictation_view.build())

if __name__ == "__main__":
    ft.app(target=main)
```

### 2. audio_engine.py - Producer-Consumer Audio Pipeline
Extract from `dictation_websocket_bridge.py`:
- Audio stream setup logic
- Convert WebSocket message sending to direct function calls
- Implement producer-consumer pattern with `queue.Queue`
- Handle STT model initialization

Key changes:
- Remove all `websocket` related code
- Replace `await websocket.send()` with direct UI update calls
- Use `asyncio.run_coroutine_threadsafe()` for thread-safe UI updates

### 3. core/stt_processor.py - Extract Parakeet Integration
From `personalparakeet/dictation.py`:
- Extract `SimpleDictation` class
- Remove any WebSocket dependencies
- Focus on: model loading, audio processing, transcription generation

### 4. core/clarity_engine.py - Direct Port
From `personalparakeet/clarity_engine.py`:
- Copy almost exactly as-is
- This code already works well
- Only change: remove any WebSocket message formatting
- Return plain text corrections instead

### 5. core/vad_engine.py - Adapt Callbacks
From `personalparakeet/vad_engine.py`:
- Port voice activity detection logic
- Change callback pattern from WebSocket to direct function calls
- Maintain pause detection timing logic

### 6. ui/dictation_view.py - Create Flet UI Component
Based on understanding `DictationView.tsx`:
- Create floating, transparent window
- Real-time transcript display area
- Status indicators (connection, recording)
- Draggable functionality
- Material Design styling

Key Flet widgets to use:
- `ft.Container` for main window with transparency
- `ft.Text` for transcript display
- `ft.Row`/`ft.Column` for layout
- `ft.GestureDetector` for dragging

### 7. config.py - Modern Configuration
From `personalparakeet/config_manager.py`:
- Convert to Python dataclasses with type hints
- Use Flet's client storage for persistence
- Remove JSON file dependency

## Code Transformation Patterns

### Pattern 1: WebSocket Message → Direct Function Call
**OLD (v2):**
```python
await websocket.send(json.dumps({
    "type": "transcription", 
    "data": {"text": text}
}))
```

**NEW (v3):**
```python
await dictation_view.update_transcript(text)
```

### Pattern 2: React State → Flet Reactive Components
**OLD (v2 - TypeScript):**
```typescript
const [transcript, setTranscript] = useState('')
setTranscript(newText)
```

**NEW (v3 - Python):**
```python
self.transcript_text = ft.Text("")
async def update_transcript(self, text):
    self.transcript_text.value = text
    await self.page.update_async()
```

### Pattern 3: Process Management → Threading
**OLD (v2):**
```python
# Complex process spawning and WebSocket server
backend_proc = subprocess.Popen([...])
```

**NEW (v3):**
```python
# Simple thread for STT processing
stt_thread = threading.Thread(target=self.stt_worker, daemon=True)
stt_thread.start()
```

## Critical Requirements

### Threading Safety
- Use `asyncio.run_coroutine_threadsafe()` for UI updates from worker threads
- Implement proper queue-based producer-consumer pattern
- Ensure clean shutdown of all threads

### UI Requirements  
- Maintain visual design: transparent, glass morphism effect
- Preserve functionality: draggable, always-on-top, adaptive sizing
- Real-time updates: <100ms transcript display latency

### Feature Preservation
- All text correction rules from Clarity Engine
- Voice activity detection with pause timing
- Configuration persistence (audio device, VAD settings)
- Future Command Mode and Thought-Linking hooks

## Dependencies for requirements-v3.txt
```
# Core Flet and audio
flet>=0.21.0
sounddevice>=0.4.6  
numpy>=1.24.0

# STT Model (from current requirements.txt)
torch>=2.0.0
nemo_toolkit[asr]>=1.19.0

# Optional: packaging
pyinstaller>=5.0
```

## Testing Validation
After creating v3 structure:
1. `python main.py` should open a Flet window
2. Window should be transparent and draggable
3. Audio pipeline should initialize without errors
4. Mock transcript should display in UI
5. No WebSocket or process management errors

## Success Criteria
- Single `python main.py` command launches everything
- No separate UI compilation or process management
- All v2 core functionality preserved in new architecture
- Clean, maintainable Python-only codebase
- Ready for incremental feature development

## Output Format
Please create all files in the specified structure and provide a summary of:
1. What code was successfully ported
2. What functionality needs additional work
3. Any architecture decisions made during porting
4. Recommended next steps for completing the migration

---

**NOTE**: This reorganization is the critical first step to eliminate the "process management nightmare" and create a stable, deployable PersonalParakeet v3.