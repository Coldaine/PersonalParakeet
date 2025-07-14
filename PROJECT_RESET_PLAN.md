# Parakeet Dictation Project - Reset and Refocus Plan

## 🎯 Project Vision Recap

**Core Goal**: Build a real-time dictation system that solves the "rewriting delay" problem - where transcriptions keep changing and confusing users (like SpeechPulse's 10-15 second correction cycles).

**Key Differentiator**: Intelligent "committed vs pending" text logic that prevents jarring rewrites while maintaining accuracy.

**Scope**: Enhanced prototype with comprehensive technical features, implementable by an AI agent in a single session.

## ✅ Original Research-Backed Decisions (Still Valid)

### Technology Stack
- **Speech Engine**: NVIDIA Parakeet (6.05% WER vs Whisper's ~8-10%)
- **Implementation Path**: Community wrappers preferred over full NVIDIA NeMo
- **Hardware**: Dual GPU utilization (RTX 5090 + RTX 3090)
- **VAD**: Dual system (Silero + WebRTC) for robustness
- **LLM**: Ollama integration for post-processing refinement
- **Audio Config**: 44.1kHz/16-bit capture, downsample to 16kHz for ASR

### Core Features (Priority Order)
1. **LocalAgreement buffering** - The main innovation solving rewriting delays
2. **Smart text injection** - Paste for editors, type for browsers
3. **Hotkey-triggered LLM refinement** - F5 for context-aware cleanup
4. **System-wide dictation** - Works across all applications
5. **Real-time status feedback** - Transparent overlay showing status

### Performance Targets
- **Latency**: 150-700ms acceptable for dictation use
- **Accuracy**: Leverage Parakeet's superior WER performance
- **GPU Utilization**: Parakeet on GPU 0, Ollama on GPU 1
## 🚨 Where We Went Wrong - Scope Creep Analysis

### 1. **Over-Engineering the Implementation**
**Original**: Use community wrappers to avoid NVIDIA complexity
**Actual**: Implemented full NVIDIA NeMo integration (`nemo-toolkit[asr]`)
**Impact**: Added complexity you don't have expertise to debug

### 2. **Package Structure Overkill**
**Original**: Enhanced prototype, single-session implementable
**Actual**: Full Python package with setup.py, entry points, PyPI-ready structure
**Impact**: Files scattered everywhere, focus lost on core functionality

### 3. **Missing Core Feature**
**Original**: LocalAgreement-n policy as primary differentiator
**Actual**: No evidence of committed/pending text logic implementation
**Impact**: Building everything except the main innovation

### 4. **Testing Complexity**
**Original**: Simple validation of working system
**Actual**: Elaborate test infrastructure that doesn't run automatically
**Impact**: Can't quickly verify basic functionality

## 🔥 Current Blocking Issues

### Primary Blocker: Windows Audio Integration Failure
- **Parakeet transcription works** - Not the problem
- **Audio capture fails on Windows** - Specific integration issue
- **No isolated testing** - Can't debug audio separately
- **System doesn't launch** - Prevents any real-world validation

### Secondary Issues
- **No committed/pending text logic** - Core feature missing
- **Package complexity** - Hard to modify and test quickly
- **EXE packaging focus** - Premature optimization before basic functionality
## 🎯 Reset Strategy - Back to Focused Implementation

### Phase 1: Prove Audio Capture (Immediate - 1 day)
**Goal**: Get basic audio input working on Windows

**Approach**: Single-file audio tester
```python
# test_audio_minimal.py
import sounddevice as sd
import numpy as np

def test_windows_audio():
    # List devices
    devices = sd.query_devices()
    print("Available devices:", devices)
    
    # Test basic capture
    duration = 5
    audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1)
    sd.wait()
    print(f"Captured {len(audio)} samples, max level: {np.max(np.abs(audio))}")
    
    return audio

if __name__ == "__main__":
    test_windows_audio()
```

**Success Criteria**: Can capture 5 seconds of audio and see non-zero amplitude

### Phase 2: Minimal Working Dictation (2 days)
**Goal**: End-to-end dictation with Parakeet, no fancy features

**Structure**: Single file implementation
```python
# dictation_minimal.py - Everything in one file for now
class MinimalDictation:
    def __init__(self):
        self.parakeet_model = load_parakeet()  # Your working implementation
        self.is_recording = False
        
    def start_recording(self):
        # Basic audio capture loop
        # Feed to Parakeet
        # Output to keyboard.write()
        
    def toggle_with_f4(self):
        # Simple hotkey handling
```

**Success Criteria**: 
- F4 starts/stops dictation
- Speech appears as text in any application
- Works on Windows
### Phase 3: Add Core Innovation (1-2 days)
**Goal**: Implement the LocalAgreement buffering logic

**Approach**: Add committed/pending text tracking
```python
class CommittedTextBuffer:
    def __init__(self, agreement_threshold=3):
        self.pending_text = ""
        self.committed_text = ""
        self.agreement_count = 0
        self.last_agreed_prefix = ""
        
    def update_transcription(self, new_text):
        # LocalAgreement-n logic
        # Commit text when n consecutive updates agree on prefix
        # Display committed + pending separately
```

**Success Criteria**:
- Can distinguish between "final" and "provisional" text
- No jarring rewrites of previously committed text
- Clear visual indication of text stability

### Phase 4: Integration Polish (1 day)
**Goal**: Add planned integrations without breaking core functionality

**Features**:
- Ollama LLM refinement (F5 hotkey)
- Smart text injection (paste vs type)
- Basic status overlay
- Dual GPU utilization

## 🔧 Immediate Action Plan

### Step 1: Diagnose Windows Audio (Today)
Create and run the minimal audio test:
1. Run `test_audio_minimal.py` on Windows
2. Document exact error messages
3. Check Windows microphone permissions
4. Try different audio devices if available

### Step 2: Create Minimal Dictation File (Tomorrow)
Based on audio test results:
1. Create single-file dictation system
2. Use your working Parakeet implementation
3. Add basic keyboard output
4. Test end-to-end on Windows

### Step 3: Implement LocalAgreement Logic (Next)
Once basic dictation works:
1. Add buffering logic for committed vs pending text
2. Test with various speech patterns
3. Tune agreement threshold for best experience
## 🚫 What We're NOT Doing (Yet)

- **Package structure** - Single files until it works
- **Complex testing** - Manual validation only
- **EXE packaging** - After core features work
- **WebSocket servers** - Unnecessary complexity
- **Extensive documentation** - Focus on working code
- **Multiple model options** - One model, make it work

## 📋 Success Metrics for Reset

### Immediate (1 week)
- [ ] Audio capture works on Windows
- [ ] Basic dictation produces text in applications
- [ ] F4 hotkey starts/stops reliably
- [ ] No crashes during normal use

### Core Feature (2 weeks)
- [ ] LocalAgreement buffering prevents text rewrites
- [ ] Clear visual distinction between committed/pending text
- [ ] Demonstrably better user experience than standard STT

### Integration (3 weeks)
- [ ] LLM refinement improves text quality
- [ ] Smart injection works across different applications
- [ ] System performs well under normal usage patterns

## 🎯 Key Principles for Reset

1. **Simplicity First**: Single files, inline code, minimal dependencies
2. **Windows Validation**: Every change must work on target platform
3. **Core Feature Focus**: LocalAgreement logic is the primary differentiator
4. **Incremental Testing**: Validate each step before adding complexity
5. **No Premature Optimization**: Package structure and EXE after it works

## 🤝 Next Steps

1. **Create minimal audio test** and run on Windows
2. **Share exact error messages** from Windows testing
3. **Build single-file dictation prototype** based on test results
4. **Focus exclusively on getting basic capture→transcription→output working**

The good news: Your research was excellent and Parakeet transcription works. We just need to strip away the complexity, solve the Windows audio issue, and implement the core buffering logic that makes this system special.

Ready to start with the minimal audio test?