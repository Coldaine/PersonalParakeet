# PersonalParakeet v3 Architecture

## Executive Summary

PersonalParakeet v3 represents a complete architectural overhaul from the problematic two-process Tauri/WebSocket system to a unified single-process Flet application. This migration addresses critical stability issues while preserving all v2 features.

**Key Decision**: Single-process Python application using Flet for UI, eliminating all inter-process communication complexity.

---

## Architecture Decision Record

**Date**: July 26, 2025  
**Status**: Accepted  
**Decision**: Migrate PersonalParakeet to a single-process Flet application.

### Context and Problem

PersonalParakeet v2 architecture led to critical issues:
- **Process synchronization failures** - WebSocket race conditions between frontend/backend
- **Complex deployment** - Requires Node.js, Rust, and Python toolchains
- **Shell/path conflicts** - npm using Git Bash causing startup failures
- **User feedback** - "Process management nightmare"

### Decision Rationale

#### Considered Alternatives

1. **Fix Current Architecture** ❌
   - Pros: Preserves existing code
   - Cons: Fundamental architectural flaws remain
   - Verdict: Treating symptoms, not the disease

2. **pywebview** 🤔
   - Pros: Preserves React UI, single process
   - Cons: Still requires JavaScript maintenance
   - Verdict: Good option but not optimal

3. **Flet** ✅ **CHOSEN**
   - Pros: Pure Python, single process, Material Design, simple deployment
   - Cons: Complete UI rewrite, larger bundle (~50MB)
   - Verdict: Best balance of simplicity and functionality

4. **Native UI** ❌
   - Pros: Smaller executable
   - Cons: Dated appearance, poor developer experience
   - Verdict: Not suitable for modern application

---

## Technical Architecture

### Before (v2) - Multi-Process
```
[Tauri Process]                    [Python Process]
├── React UI          <-WS->      ├── WebSocket Server
├── Window Management              ├── Parakeet STT
└── IPC Bridge                     └── Audio Processing
```
**Problems**: Race conditions, complex startup, deployment nightmare

### After (v3) - Single Process
```
[Single Python Process]
├── Flet UI (Main Thread)
├── Audio Producer Thread  
├── STT Consumer Thread
└── Shared Queue (thread-safe)
```
**Benefits**: Simple, reliable, maintainable

---

## Design Principles

### 1. Simplicity First
- **One language**: Python only
- **One process**: No IPC complexity
- **One executable**: PyInstaller bundle

### 2. Thread Safety
- **Producer-consumer pattern** with `queue.Queue`
- **Async UI updates** via `asyncio.run_coroutine_threadsafe()`
- **No direct cross-thread UI access**

### 3. Robustness
- **Graceful degradation** - Mock STT if ML unavailable
- **Error isolation** - Thread failures don't crash app
- **Resource management** - Proper cleanup on shutdown

---

## Threading Model

### Main Thread (Flet UI)
- Handles all UI updates and user interactions
- Manages application lifecycle
- Coordinates feature state

### Audio Producer Thread
- Managed by sounddevice callback
- Minimal processing - only queue audio chunks
- Runs at audio sample rate (16kHz)

### STT Consumer Thread
- Pulls audio chunks from queue
- Runs Parakeet inference (GPU/CPU)
- Sends results to main thread via async calls

### Thread Communication
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

---

## Critical Architecture Constraints

### ❌ FORBIDDEN PATTERNS
These will break the v3 architecture:
- WebSocket servers or clients
- subprocess calls for UI components  
- Multi-process architecture
- Direct cross-thread UI access
- Any Tauri/React/Node.js dependencies

### ✅ REQUIRED PATTERNS
Single-process Flet architecture:
- Producer-consumer with `queue.Queue`
- `asyncio.run_coroutine_threadsafe()` for UI updates
- Dataclass-based configuration
- Direct function calls between components

---

## Key Architectural Components

### Configuration System
```python
@dataclass
class AppConfig:
    # Audio settings
    audio_device_index: Optional[int] = None
    sample_rate: int = 16000
    
    # VAD settings
    vad_threshold: float = 0.01
    pause_duration_ms: int = 1500
    
    # STT settings
    use_mock_stt: bool = False
    stt_device: str = "cuda"
    
    # UI settings
    window_opacity: float = 0.9
    always_on_top: bool = True
```

### Audio Pipeline
- **Capture**: sounddevice with callback-based streaming
- **Processing**: queue-based producer-consumer
- **VAD**: Real-time voice activity detection
- **STT**: NVIDIA Parakeet-TDT with GPU acceleration

### UI Framework
- **Flet**: Python-native Material Design
- **Glass morphism**: Transparent blur effects
- **Responsive**: Adaptive sizing and positioning
- **Cross-platform**: Windows primary, Linux secondary

---

## Lessons Learned from v2

### What Went Wrong
1. **WebSocket Complexity**: Bidirectional communication introduced race conditions
2. **Process Management**: Starting/stopping multiple processes unreliably
3. **Deployment Hell**: Three different runtimes (Node.js, Rust, Python)
4. **State Synchronization**: Frontend/backend state drift
5. **Error Propagation**: Failures in one process crashed entire system

### Key Insights
- **Simpler is better**: Reduce architectural complexity
- **Single responsibility**: Each thread has one job
- **Fail fast**: Better to crash early than corrupt state
- **Local first**: Direct function calls over network protocols

---

## Success Criteria

### Functional Requirements
- ✅ All v2 features preserved
- ✅ <150ms end-to-end latency
- ✅ Single-click launch
- ✅ No startup failures
- ✅ Cross-platform compatibility

### Technical Requirements
- ✅ Single Python process
- ✅ Memory usage <4GB during extended sessions
- ✅ Graceful error handling and recovery
- ✅ Thread-safe UI updates
- ✅ Clean shutdown of all threads

### User Experience Requirements
- ✅ Transparent, draggable UI
- ✅ Real-time transcription display
- ✅ Visual status indicators
- ✅ Natural dictation flow

---

## Risk Mitigation

### Identified Risks
1. **Flet performance with real-time updates**
   - Mitigation: Batch UI updates, use async patterns
   
2. **PyInstaller bundle size with ML models**
   - Mitigation: Optional ML dependencies, model compression
   
3. **Cross-platform compatibility**
   - Mitigation: Test on Linux/Windows, platform-specific injection
   
4. **Feature regression from v2**
   - Mitigation: Comprehensive feature parity testing

### Monitoring
- Performance metrics during development
- Memory usage profiling
- Cross-platform testing matrix
- User acceptance testing

---

## Future Considerations

### Planned Enhancements
- Multi-language support
- Cloud configuration sync  
- Advanced audio preprocessing
- Plugin architecture for custom corrections

### Technology Evolution
- Watch Flet development for new features
- Monitor PyTorch/NeMo updates for performance
- Consider ONNX for model optimization
- Evaluate WebGPU for broader GPU support

---

**Decision Review**: This architecture will be evaluated after 4 weeks of development. Success metrics must be met for continued development in this direction.