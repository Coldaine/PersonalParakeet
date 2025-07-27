# PersonalParakeet v3: Architecture and Migration Guide

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Architecture Decision Record](#architecture-decision-record)
   - [Context and Problem](#context-and-problem)
   - [Decision and Alternatives](#decision-and-alternatives)
   - [Technical Comparison](#technical-comparison)
3. [Implementation Plan](#implementation-plan)
   - [Phase 1: Core Foundation](#phase-1-core-foundation-week-1)
   - [Phase 2: STT Integration](#phase-2-stt-integration-week-1-2)
   - [Phase 3: Core Features Port](#phase-3-core-features-port-week-2)
   - [Phase 4: Advanced Features](#phase-4-advanced-features-week-3)
   - [Phase 5: Deployment](#phase-5-deployment--distribution-week-3-4)
4. [Code Reorganization Instructions](#code-reorganization-instructions)
   - [New v3 Structure](#new-v3-structure)
   - [Porting Instructions](#specific-porting-instructions)
   - [Code Transformation Patterns](#code-transformation-patterns)
5. [Technical Specifications](#technical-specifications)
   - [Threading Architecture](#threading-architecture)
   - [Key Design Patterns](#key-design-patterns)
   - [Configuration Schema](#configuration-schema)
6. [Success Criteria and Validation](#success-criteria-and-validation)

---

## Executive Summary

PersonalParakeet v3 represents a complete architectural overhaul from the problematic two-process Tauri/WebSocket system to a unified single-process Flet application. This migration addresses critical stability issues while preserving all v2 features including the Dictation View, Clarity Engine, and Voice Activity Detection.

**Key Decision**: Migrate to Flet for a pure Python, single-process solution that eliminates all IPC complexity.

**Timeline**: 4 weeks from deprecated v2 to production-ready v3

**Deliverable**: Single executable < 100MB with all v2 features, but stable and maintainable

---

## Architecture Decision Record

**Date**: July 21, 2025  
**Status**: Accepted  
**Technical Story**: PersonalParakeet v2's two-process WebSocket architecture proved unstable and overly complex, requiring a fundamental architectural change.

### Context and Problem

PersonalParakeet v2 architecture led to critical issues:
- Process synchronization failures
- WebSocket connection race conditions  
- Complex deployment requiring Node.js, Rust, and Python toolchains
- Shell/path conflicts preventing reliable startup
- "Process management nightmare" (user quote)

### Decision and Alternatives

**Decision**: We will migrate PersonalParakeet to a single-process Flet application.

#### Considered Alternatives

1. **Fix Current Architecture** (Rejected)
   - Pros: Preserves existing code
   - Cons: Fundamental flaws remain
   - Verdict: Treating symptoms, not the disease

2. **pywebview** (Considered)
   - Pros: Preserves React UI, single process
   - Cons: Still requires JavaScript maintenance
   - Verdict: Good option but not optimal

3. **Flet** (Accepted) ✅
   - Pros: Pure Python, single process, Material Design, simple deployment
   - Cons: Complete UI rewrite, larger bundle (~50MB)
   - Verdict: Best balance of simplicity and functionality

4. **Full Native** (Rejected)
   - Pros: Native performance
   - Cons: Dated UI, poor developer experience
   - Verdict: Not suitable for modern application

### Technical Comparison

#### Before (v2)
```
[Tauri Process]                    [Python Process]
├── React UI          <-WS->      ├── WebSocket Server
├── Window Management              ├── Parakeet STT
└── IPC Bridge                     └── Audio Processing
```

#### After (v3)
```
[Single Python Process]
├── Flet UI (Main Thread)
├── Audio Producer Thread  
├── STT Consumer Thread
└── Shared Queue (thread-safe)
```

---

## Implementation Plan

### Phase 1: Core Foundation (Week 1)

**Goal**: Establish basic Flet application with audio capture

#### Tasks
- [ ] Create new project structure
- [ ] Set up virtual environment and dependencies
- [ ] Create main.py with basic Flet window
- [ ] Implement producer-consumer audio pattern
- [ ] Create AudioEngine class with queue.Queue
- [ ] Build basic UI components (floating window, transcript display)

**Deliverable**: Basic dictation app with audio capture and placeholder text

### Phase 2: STT Integration (Week 1-2)

**Goal**: Integrate Parakeet-TDT model with proper threading

#### Tasks
- [ ] Port SimpleDictation class to new architecture
- [ ] Implement model lazy loading with CUDA/CPU detection
- [ ] Set up thread-safe UI updates with asyncio
- [ ] Add frame batching and performance monitoring

**Deliverable**: Working STT with real-time transcription display

### Phase 3: Core Features Port (Week 2)

**Goal**: Migrate v2 features to Flet architecture

#### Tasks
- [ ] Port clarity_engine.py with minimal changes
- [ ] Port vad_engine.py with adapted callbacks
- [ ] Create settings dialog with Flet client storage
- [ ] Add audio device selection and configuration

**Deliverable**: Feature parity with v2 but stable

### Phase 4: Advanced Features (Week 3)

**Goal**: Implement Command Mode and Intelligent Thought-Linking

#### Tasks
- [ ] Implement "Parakeet Command" activation
- [ ] Port thought detection logic
- [ ] Add UI polish (animations, glass morphism)
- [ ] Create multiple theme options

**Deliverable**: Full v2 feature set in stable Flet implementation

### Phase 5: Deployment & Distribution (Week 3-4)

**Goal**: Create distributable executable

#### Tasks
- [ ] Configure PyInstaller with all assets
- [ ] Create Inno Setup installer for Windows
- [ ] Test on clean systems
- [ ] Write user documentation

**Deliverable**: Professional installer for PersonalParakeet v3

---

## Code Reorganization Instructions

### New v3 Structure

```
v3-flet/
├── main.py                    # Flet app entry point
├── audio_engine.py            # Producer-consumer audio pipeline
├── config.py                  # Dataclass-based config
├── requirements-v3.txt        # Simplified dependencies
├── ui/
│   ├── __init__.py
│   ├── dictation_view.py      # Main Flet UI component
│   ├── components.py          # Reusable Flet widgets  
│   └── theme.py               # Material Design theme
├── core/
│   ├── __init__.py
│   ├── stt_processor.py       # Extract from dictation.py
│   ├── clarity_engine.py      # Direct copy with minor updates
│   ├── vad_engine.py          # Direct copy with minor updates
│   └── thought_linker.py      # Extract thought-linking logic
└── assets/
    └── icon.ico               # App icon
```

### Specific Porting Instructions

#### 1. main.py - Flet Application Entry Point
```python
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

#### 2. audio_engine.py - Producer-Consumer Pipeline
Extract from `dictation_websocket_bridge.py`:
- Remove all WebSocket code
- Replace `await websocket.send()` with direct UI calls
- Use `asyncio.run_coroutine_threadsafe()` for thread safety

#### 3. Core Module Ports
- **stt_processor.py**: Extract SimpleDictation from dictation.py
- **clarity_engine.py**: Direct port, remove WebSocket formatting
- **vad_engine.py**: Port logic, adapt callbacks to direct calls

#### 4. UI Components
Based on React components, create Flet equivalents:
- Floating transparent window
- Real-time transcript display
- Status indicators
- Draggable functionality

### Code Transformation Patterns

#### WebSocket Message → Direct Function Call
```python
# OLD (v2)
await websocket.send(json.dumps({
    "type": "transcription", 
    "data": {"text": text}
}))

# NEW (v3)
await dictation_view.update_transcript(text)
```

#### React State → Flet Reactive Components
```python
# OLD (v2 - TypeScript)
const [transcript, setTranscript] = useState('')

# NEW (v3 - Python)
self.transcript_text = ft.Text("")
async def update_transcript(self, text):
    self.transcript_text.value = text
    await self.page.update_async()
```

#### Process Management → Threading
```python
# OLD (v2)
backend_proc = subprocess.Popen([...])

# NEW (v3)
stt_thread = threading.Thread(target=self.stt_worker, daemon=True)
stt_thread.start()
```

---

## Technical Specifications

### Threading Architecture

```python
# Main Thread (Flet UI)
- Handles all UI updates
- Manages user interactions
- Coordinates feature state

# Audio Producer Thread
- Managed by sounddevice
- Minimal processing
- Only puts data in queue

# STT Consumer Thread  
- Pulls from audio queue
- Runs Parakeet inference
- Sends results to main thread
```

### Key Design Patterns

#### Producer-Consumer Audio Pipeline
```python
class AudioEngine:
    def __init__(self):
        self.audio_queue = queue.Queue(maxsize=50)
        self.running = True
    
    def audio_callback(self, indata, frames, time, status):
        """Producer - runs in sounddevice thread"""
        if status:
            print(status)
        self.audio_queue.put(indata.copy())
    
    def stt_worker(self, page):
        """Consumer - runs in dedicated thread"""
        while self.running:
            audio_chunk = self.audio_queue.get()
            text = self.stt_model.transcribe(audio_chunk)
            
            # Thread-safe UI update
            asyncio.run_coroutine_threadsafe(
                self.update_ui(text), 
                page.loop
            )
```

#### Flet Reactive State
```python
class DictationView:
    def __init__(self, page):
        self.transcript = ft.Text("", selectable=True)
        self.status = ft.Icon(
            ft.icons.CIRCLE, 
            color=ft.colors.GREEN
        )
        
    async def update_transcript(self, text):
        self.transcript.value = text
        await self.transcript.update_async()
```

### Configuration Schema
```python
@dataclass
class AppConfig:
    # Audio settings
    audio_device_index: Optional[int] = None
    sample_rate: int = 16000
    
    # VAD settings
    vad_threshold: float = 0.01
    pause_duration_ms: int = 1500
    
    # Clarity settings
    clarity_enabled: bool = True
    
    # UI settings
    window_opacity: float = 0.9
    always_on_top: bool = True
    theme_mode: str = "dark"
```

### Dependencies (requirements-v3.txt)
```
# Core Flet and audio
flet>=0.21.0
sounddevice>=0.4.6  
numpy>=1.24.0

# STT Model
torch>=2.0.0
nemo_toolkit[asr]>=1.19.0

# Optional: packaging
pyinstaller>=5.0
```

---

## Success Criteria and Validation

### Critical Requirements

1. **Threading Safety**
   - Use `asyncio.run_coroutine_threadsafe()` for UI updates
   - Implement proper queue-based producer-consumer pattern
   - Ensure clean shutdown of all threads

2. **UI Requirements**
   - Maintain visual design: transparent, glass morphism effect
   - Preserve functionality: draggable, always-on-top
   - Real-time updates: <100ms transcript display latency

3. **Feature Preservation**
   - All text correction rules from Clarity Engine
   - Voice activity detection with pause timing
   - Configuration persistence
   - Command Mode and Thought-Linking hooks

### Testing Validation

After creating v3 structure:
1. `python main.py` should open a Flet window
2. Window should be transparent and draggable
3. Audio pipeline should initialize without errors
4. Mock transcript should display in UI
5. No WebSocket or process management errors

### Success Metrics

- [ ] Single-click launch
- [ ] No startup failures
- [ ] All v2 features working
- [ ] <2 second startup time
- [ ] Single executable < 100MB
- [ ] Improved UI responsiveness

### Risk Mitigation

1. **Flet performance with real-time updates**
   - Mitigation: Batch UI updates, use async updates
   
2. **PyInstaller bundle size with ML models**
   - Mitigation: Compress models, offer lite version
   
3. **Cross-platform compatibility**
   - Mitigation: Test early on Linux/macOS VMs

4. **Feature regression**
   - Mitigation: Comprehensive test checklist

---

## Conclusion

This migration represents a fundamental shift from a fragile, complex multi-process architecture to a robust, simple single-process design. By choosing Flet, we eliminate entire categories of problems while maintaining all the features that make PersonalParakeet valuable.

**The key insight: Simpler is better. One language, one process, one executable.**

Decision will be reviewed after Phase 1 implementation. If Flet proves inadequate, pywebview remains as fallback option.