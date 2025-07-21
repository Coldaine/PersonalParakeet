# PersonalParakeet v3: Flet Refactor Implementation Plan

## Executive Summary

This document outlines the complete refactoring of PersonalParakeet from the problematic two-process Tauri/WebSocket architecture to a unified single-process Flet application. This refactor addresses all critical issues identified in the architectural review while preserving core v2 features.

### Key Decision: Why Flet?

After extensive analysis and user feedback, Flet was chosen because:
- **Single Process**: Eliminates all IPC complexity and race conditions
- **Pure Python**: No JavaScript, no Rust, no toolchain conflicts
- **Simple Deployment**: Single executable with PyInstaller
- **Material Design**: Professional UI out of the box
- **Cross-platform**: Windows primary, Linux/macOS ready

## Architecture Overview

### Current Architecture (v2) - DEPRECATED
```
[Tauri Process] <-- WebSocket --> [Python Process]
     |                                    |
  React UI                          Parakeet STT
```

### New Architecture (v3) - Flet
```
[Single Python Process]
    ├── Flet UI (Main Thread)
    ├── Audio Producer Thread
    ├── STT Consumer Thread
    └── Shared Queue (thread-safe)
```

## Implementation Phases

### Phase 1: Core Foundation (Week 1)
**Goal**: Establish basic Flet application with audio capture

#### 1.1 Project Setup
- [ ] Create new project structure
- [ ] Set up virtual environment
- [ ] Install core dependencies: `flet`, `sounddevice`, `numpy`
- [ ] Create main.py with basic Flet window

#### 1.2 Audio Pipeline Implementation
- [ ] Implement producer-consumer pattern
- [ ] Create AudioEngine class with queue.Queue
- [ ] Set up sounddevice callback (producer)
- [ ] Create STT worker thread (consumer)
- [ ] Add queue overflow protection

#### 1.3 Basic UI Components
- [ ] Floating dictation window with transparency
- [ ] Transcript display area
- [ ] Status indicator (green/red)
- [ ] Draggable window functionality

**Deliverable**: Basic dictation app that captures audio and displays placeholder text

### Phase 2: STT Integration (Week 1-2)
**Goal**: Integrate Parakeet-TDT model with proper threading

#### 2.1 Model Integration
- [ ] Port SimpleDictation class to new architecture
- [ ] Implement model lazy loading
- [ ] Add CUDA/CPU detection
- [ ] Handle model initialization in worker thread

#### 2.2 Thread Communication
- [ ] Implement asyncio.run_coroutine_threadsafe pattern
- [ ] Create thread-safe UI update methods
- [ ] Add error handling for model failures
- [ ] Implement graceful shutdown

#### 2.3 Performance Optimization
- [ ] Add frame batching for efficiency
- [ ] Implement adaptive queue management
- [ ] Monitor and log processing latency
- [ ] Add performance metrics display

**Deliverable**: Working STT with real-time transcription display

### Phase 3: Core Features Port (Week 2)
**Goal**: Migrate v2 features to Flet architecture

#### 3.1 Clarity Engine Integration
- [ ] Port existing clarity_engine.py
- [ ] Integrate with STT output pipeline
- [ ] Add UI indicators for corrections
- [ ] Maintain correction history

#### 3.2 Voice Activity Detection
- [ ] Port VAD engine
- [ ] Implement pause detection
- [ ] Add visual VAD indicators
- [ ] Configure VAD thresholds in UI

#### 3.3 Configuration Management
- [ ] Create settings dialog in Flet
- [ ] Use Flet client storage for persistence
- [ ] Add audio device selection
- [ ] Include all VAD/Clarity settings

**Deliverable**: Feature parity with v2 but stable

### Phase 4: Advanced Features (Week 3)
**Goal**: Implement Command Mode and Intelligent Thought-Linking

#### 4.1 Command Mode
- [ ] Implement "Parakeet Command" activation
- [ ] Create command palette UI
- [ ] Add keyboard shortcuts
- [ ] Visual mode indicators

#### 4.2 Intelligent Thought-Linking
- [ ] Port thought detection logic
- [ ] Create visual link indicators
- [ ] Implement storage backend
- [ ] Add link navigation UI

#### 4.3 UI Polish
- [ ] Implement smooth animations
- [ ] Add glass morphism effects
- [ ] Create multiple theme options
- [ ] Optimize window positioning

**Deliverable**: Full v2 feature set in stable Flet implementation

### Phase 5: Deployment & Distribution (Week 3-4)
**Goal**: Create distributable executable

#### 5.1 PyInstaller Configuration
- [ ] Create .spec file with all assets
- [ ] Bundle Parakeet model efficiently
- [ ] Optimize executable size
- [ ] Add application icon and metadata

#### 5.2 Installer Creation
- [ ] Use Inno Setup for Windows installer
- [ ] Create start menu shortcuts
- [ ] Add uninstaller
- [ ] Include README and license

#### 5.3 Testing & Documentation
- [ ] Test on clean Windows systems
- [ ] Create user documentation
- [ ] Record demo video
- [ ] Write troubleshooting guide

**Deliverable**: Professional installer for PersonalParakeet v3

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

## Migration Guide

### For Developers
1. **Stop all v2 development** on Tauri/WebSocket architecture
2. **Clone this plan** to new `personal-parakeet-flet` directory
3. **Preserve** the following from v2:
   - `clarity_engine.py` (minimal changes needed)
   - `vad_engine.py` (adapt callbacks)
   - Parakeet model configuration
4. **Discard**:
   - All WebSocket code
   - React UI components
   - Tauri configuration

### For Users
1. **v2 will be deprecated** - no further updates
2. **v3 installer** will be single-file download
3. **Settings migration** will be automatic
4. **No prerequisites** - works out of the box

## Risk Mitigation

### Identified Risks
1. **Flet performance with real-time updates**
   - Mitigation: Batch UI updates, use async updates
   
2. **PyInstaller bundle size with ML models**
   - Mitigation: Compress models, offer lite version
   
3. **Cross-platform compatibility**
   - Mitigation: Test early on Linux/macOS VMs

4. **Feature regression**
   - Mitigation: Comprehensive test checklist

## Success Criteria

1. **Single command/click launch** ✓
2. **No WebSocket/IPC errors** ✓
3. **Sub-second startup time** ✓
4. **Single distributable file** ✓
5. **All v2 features working** ✓
6. **Improved UI responsiveness** ✓

## Timeline

- **Week 1**: Core foundation + Basic STT
- **Week 2**: Feature migration + Polish  
- **Week 3**: Advanced features + Testing
- **Week 4**: Deployment + Documentation

Total: **4 weeks** from deprecated v2 to production-ready v3

## Conclusion

This refactor represents a fundamental shift from a fragile, complex multi-process architecture to a robust, simple single-process design. By choosing Flet, we eliminate entire categories of problems while maintaining all the features that make PersonalParakeet valuable.

The key insight: **Simpler is better**. One language, one process, one executable.