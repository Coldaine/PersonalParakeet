# PersonalParakeet v1 to v2 Integration Plan

## Overview
This document outlines the transition strategy from the current LocalAgreement buffering system (v1) to the new Workshop Model (v2), ensuring minimal disruption for existing users.

## Current State Analysis (v1)

### What Works Well
- **Parakeet STT Integration**: Already optimized for RTX 5090
- **Audio Pipeline**: Stable real-time audio capture with sounddevice
- **Hotkey System**: F4 toggle is intuitive and reliable
- **Cross-platform Support**: Windows primary, Linux secondary

### What Needs Enhancement
- **Text Stability**: LocalAgreement prevents rewrites but feels "invisible"
- **User Feedback**: No visual indication of processing state
- **Complex Logic**: LocalAgreement algorithm is hard to debug/maintain
- **Limited Control**: Users can't easily manage misrecognitions

## Migration Strategy

### Phase 1: Parallel Development (Weeks 1-4)
Keep v1 fully functional while building v2 components:

```python
# New project structure
personalparakeet/
├── v1/                        # Current system (preserved)
│   ├── dictation.py
│   ├── local_agreement.py
│   └── text_injection.py
├── v2/                        # New Workshop Model
│   ├── workshop_box.py
│   ├── clarity_engine.py
│   └── thought_linking.py
├── common/                    # Shared components
│   ├── audio_capture.py
│   ├── stt_engine.py        # Parakeet integration
│   └── hotkey_manager.py
└── __main__.py               # Mode selector
```

### Phase 2: Component Extraction (Week 1)

Extract reusable components from v1:

1. **Audio Pipeline**
   ```python
   # Extract from dictation.py
   class AudioProcessor:
       def __init__(self, device_index=None):
           self.stream = None
           self.sample_rate = 16000
           self.chunk_duration = 1.0
       
       def start_capture(self, callback):
           # Existing audio capture logic
   ```

2. **STT Integration**
   ```python
   # Extract Parakeet model handling
   class ParakeetSTT:
       def __init__(self):
           self.model = self._load_model()
       
       def transcribe(self, audio_chunk):
           # Existing transcription logic
   ```

3. **Hotkey Management**
   ```python
   # Make hotkey system mode-agnostic
   class HotkeyManager:
       def register(self, key, callback):
           # Support both v1 and v2 callbacks
   ```

### Phase 3: Workshop Box Implementation (Weeks 2-3)

Build the new UI components while reusing core infrastructure:

```python
class WorkshopDictation(SimpleDictation):  # Inherit from v1
    def __init__(self):
        super().__init__()
        self.workshop_box = WorkshopBox()
        self.clarity_engine = ClarityEngine()
        
    def process_audio(self, audio_chunk):
        # Use existing STT
        raw_text = self.model.transcribe(audio_chunk)
        
        # New: Apply Clarity Engine
        corrected_text = self.clarity_engine.correct(raw_text)
        
        # New: Update Workshop Box instead of LocalAgreement
        self.workshop_box.update_text(corrected_text)
```

### Phase 4: Feature Parity Checklist

Ensure v2 maintains all v1 capabilities:

| Feature | v1 Implementation | v2 Implementation | Status |
|---------|-------------------|-------------------|---------|
| F4 Toggle | ✓ keyboard.add_hotkey | ✓ Reuse HotkeyManager | Ready |
| RTX 5090 Support | ✓ CUDA 12.8 | ✓ Same PyTorch config | Ready |
| Text Injection | ✓ Windows APIs | ✓ Enhanced with visual feedback | TODO |
| Continuous Mode | ✓ LocalAgreement | ✓ Workshop Box + Thought Linking | TODO |
| Linux Support | ✓ Basic | ✓ Improved with Qt | TODO |

### Phase 5: User Migration (Weeks 9-10)

1. **Soft Launch**
   ```python
   # In __main__.py
   if "--v2" in sys.argv or os.environ.get("PARAKEET_V2"):
       from personalparakeet.v2 import WorkshopDictation as Dictation
   else:
       from personalparakeet.v1 import SimpleDictation as Dictation
   ```

2. **Configuration Migration**
   ```python
   def migrate_config(v1_config):
       return {
           # Map v1 settings to v2
           "workshop_box": {
               "opacity": 0.88,
               "position": "cursor",  # or "fixed"
               "auto_commit_delay": v1_config.get("pause_threshold", 1.5)
           },
           "clarity_engine": {
               "enabled": True,
               "model": "phi-3-mini"
           },
           # Preserve v1 settings
           "audio": v1_config.get("audio", {}),
           "hotkeys": v1_config.get("hotkeys", {})
       }
   ```

3. **Fallback Mode**
   - Keep "Classic Mode" option in settings
   - Allow instant switching between v1/v2
   - Collect telemetry on mode usage

## Risk Mitigation

### Performance Concerns
- **Risk**: Clarity Engine adds latency
- **Mitigation**: 
  - Implement async correction pipeline
  - Cache common corrections
  - Offer "Fast Mode" without Clarity Engine

### Visual Distraction
- **Risk**: Workshop Box is too prominent
- **Mitigation**:
  - Configurable opacity/size
  - "Minimal Mode" with tiny indicator
  - Keyboard shortcut to hide temporarily

### Learning Curve
- **Risk**: New UI paradigm confuses users
- **Mitigation**:
  - Interactive tutorial on first launch
  - Video demonstrations
  - Gradual feature introduction

## Success Metrics

### Technical Metrics
- Transcription latency: ≤ 200ms (maintain v1 performance)
- UI frame rate: ≥ 60 FPS
- Memory usage: < 500MB (including Clarity Engine)
- CPU usage: < 15% average

### User Experience Metrics
- Mode switch rate: Track v1 vs v2 usage
- Error correction rate: Measure manual edits
- Session length: Compare v1 vs v2 engagement
- Feature adoption: Command mode, thought linking

## Rollback Plan

If v2 encounters critical issues:

1. **Immediate**: `--force-v1` flag bypasses all v2 code
2. **Hotfix**: Push update that defaults to v1
3. **Data**: Preserve v2 preferences for future retry

## Timeline Summary

- **Week 1**: Extract common components
- **Weeks 2-3**: Workshop Box implementation
- **Week 4**: Clarity Engine integration
- **Weeks 5-6**: Command mode & thought linking
- **Week 7**: Performance optimization
- **Week 8**: Cross-platform testing
- **Week 9**: Beta release with v1/v2 toggle
- **Week 10**: Documentation & tutorials

This gradual approach ensures v1 users experience no disruption while v2 features are progressively enhanced and validated.