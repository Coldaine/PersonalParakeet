# Architecture Decision Record: Migration to Flet

**Date**: July 21, 2025  
**Status**: Accepted  
**Deciders**: Development Team, User Feedback  
**Technical Story**: PersonalParakeet v2's two-process WebSocket architecture proved unstable and overly complex, requiring a fundamental architectural change.

## Context

PersonalParakeet v2 was built using:
- **Frontend**: Tauri (Rust) + React (TypeScript)
- **Backend**: Python with WebSocket server
- **Communication**: WebSocket over localhost:8765
- **Deployment**: Required separate bundling of Python sidecar

This architecture led to critical issues:
- Process synchronization failures
- WebSocket connection race conditions
- Complex deployment requiring Node.js, Rust, and Python toolchains
- Shell/path conflicts preventing reliable startup
- "Process management nightmare" (user quote)

## Decision

**We will migrate PersonalParakeet to a single-process Flet application.**

## Considered Alternatives

### 1. Fix Current Architecture (Rejected)
- **Pros**: Preserves existing code, incremental fixes possible
- **Cons**: Fundamental flaws remain, complexity persists
- **Verdict**: Treating symptoms, not the disease

### 2. pywebview (Considered)
- **Pros**: Preserves React UI, single process, proven solution
- **Cons**: Still requires JavaScript, two-language maintenance
- **Verdict**: Good option but not optimal for our needs

### 3. Flet (Accepted)
- **Pros**: 
  - Pure Python solution
  - Single process, no IPC
  - Built-in Material Design UI
  - Simple PyInstaller deployment
  - Cross-platform from single codebase
- **Cons**: 
  - Complete UI rewrite required
  - Larger bundle size (~50MB)
  - Less UI customization flexibility

### 4. Full Native (Tkinter/PyQt)
- **Pros**: Native performance, small size
- **Cons**: Dated UI, poor developer experience
- **Verdict**: Not suitable for modern application

## Consequences

### Positive
1. **Eliminated Complexity**: No WebSocket, no IPC, no process synchronization
2. **Single Language**: Pure Python reduces cognitive load
3. **Reliable Startup**: Single process = no race conditions
4. **Easy Deployment**: PyInstaller creates one executable
5. **Better Maintainability**: One codebase, one set of dependencies

### Negative
1. **UI Rewrite**: All React components must be recreated
2. **Learning Curve**: Team must learn Flet framework
3. **Bundle Size**: Flutter runtime adds ~30MB overhead
4. **Less Flexible**: Bound to Material Design patterns

### Neutral
1. **Performance**: Similar to Tauri for our use case
2. **Look and Feel**: Different but equally modern
3. **Development Speed**: Faster iteration, but initial rewrite

## Technical Details

### Architecture Comparison

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

### Key Technical Decisions

1. **Threading Model**: Producer-consumer pattern with queue.Queue
2. **UI Updates**: asyncio.run_coroutine_threadsafe for thread safety
3. **State Management**: Flet reactive components with client storage
4. **Audio Pipeline**: sounddevice with callback → queue → STT worker
5. **Deployment**: PyInstaller --onefile with Inno Setup installer

### Code Example

```python
# Before: Complex WebSocket communication
async def send_transcription(self, text):
    await self.websocket.send(json.dumps({
        "type": "transcription",
        "data": {"text": text}
    }))

# After: Direct UI update
async def update_transcript(self, text):
    self.transcript_text.value = text
    await self.page.update_async()
```

## Implementation Plan

1. **Week 1**: Core Flet app with audio pipeline
2. **Week 2**: Port all v2 features
3. **Week 3**: Polish and advanced features
4. **Week 4**: Testing and deployment

## Validation

Success criteria:
- [ ] Single-click launch
- [ ] No startup failures
- [ ] All v2 features working
- [ ] <2 second startup time
- [ ] Single executable < 100MB

## References

1. Gemini Architectural Review (July 21, 2025)
2. User Feedback: "version two is absolutely vital... this should be way more integrated and easy"
3. Flet Documentation: https://flet.dev
4. PyInstaller + Flet Guide: https://flet.dev/docs/guides/python/packaging-desktop-app

## Decision Review

This decision will be reviewed after Phase 1 implementation. If Flet proves inadequate, pywebview remains as fallback option.