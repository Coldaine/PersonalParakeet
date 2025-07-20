# Voice Activity Detection (VAD) Implementation Plan
**Task 3 - High Priority**

## Overview
Implement natural pause detection to automatically trigger "Commit & Continue" actions in the Workshop Box. This replaces manual user actions with intelligent speech pattern recognition.

## Technical Requirements

### Core VAD Components
1. **Real-time Audio Analysis** - Continuous monitoring of audio levels
2. **Silence Detection** - Identify periods of no speech activity
3. **Pause Classification** - Distinguish between natural pauses and speech endings
4. **Configurable Thresholds** - User-adjustable sensitivity settings

## Implementation Strategy

### Phase 1: Basic Silence Detection (Week 1)

#### 1.1 Audio Level Monitoring
```python
# New file: personalparakeet/vad_engine.py
class VoiceActivityDetector:
    def __init__(self, sample_rate=16000, frame_duration=0.03):
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * frame_duration)
        self.silence_threshold = 0.01  # Configurable
        self.pause_duration_threshold = 1.5  # seconds
```

#### 1.2 RMS Energy Calculation
- **Real-time RMS computation** for each audio frame
- **Sliding window smoothing** to reduce noise sensitivity
- **Adaptive threshold adjustment** based on background noise

#### 1.3 Integration Points
- **Modify `workshop_websocket_bridge.py`** to include VAD processing
- **Add VAD callbacks** to existing audio processing pipeline
- **Update Workshop Box UI** to show VAD status indicators

### Phase 2: Advanced Pause Detection (Week 2)

#### 2.1 Multi-criteria Pause Detection
```python
class AdvancedPauseDetector:
    def __init__(self):
        # Combine multiple detection methods
        self.energy_detector = EnergyBasedDetector()
        self.spectral_detector = SpectralDetector()
        self.ml_detector = MLBasedDetector()  # Optional
```

#### 2.2 Detection Algorithms
1. **Energy-based Detection**
   - RMS energy thresholds
   - Zero-crossing rate analysis
   - Short-time energy computation

2. **Spectral Analysis**
   - Spectral centroid changes
   - Spectral rolloff detection
   - High-frequency content analysis

3. **Machine Learning Approach** (Optional Advanced Feature)
   - Pre-trained VAD model (WebRTCVAD or custom)
   - Feature extraction from audio frames
   - Classification: speech/silence/pause

#### 2.3 Context-Aware Pauses
- **Breathing pattern recognition** - Distinguish breathing from speech pauses
- **Sentence boundary detection** - Longer pauses at sentence endings
- **Utterance continuation detection** - Short pauses mid-sentence

### Phase 3: Integration & Configuration (Week 3)

#### 3.1 Configuration System
```python
# Add to personalparakeet/config_manager.py
class VADConfig:
    silence_threshold: float = 0.01
    pause_duration_ms: int = 1500
    sensitivity: str = "medium"  # low/medium/high
    breathing_filter: bool = True
    adaptive_threshold: bool = True
```

#### 3.2 Workshop Box Integration
- **VAD status indicator** in UI (microphone icon states)
- **Real-time audio level visualization** 
- **Pause countdown timer** before auto-commit
- **Manual override controls** (disable VAD, force commit)

#### 3.3 WebSocket Protocol Updates
```typescript
// Add to workshop-box-ui/src/stores/transcriptionStore.ts
interface VADStatus {
  isActive: boolean;
  audioLevel: number;
  pauseDuration: number;
  willCommitIn: number; // ms until auto-commit
}
```

## Detailed Implementation Steps

### Step 1: Core VAD Engine (2-3 days)
```python
# personalparakeet/vad_engine.py
import numpy as np
from typing import Callable, Optional
import threading
import time

class VoiceActivityDetector:
    def __init__(self, 
                 sample_rate: int = 16000,
                 frame_duration: float = 0.03,
                 silence_threshold: float = 0.01,
                 pause_threshold: float = 1.5):
        
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * frame_duration)
        self.silence_threshold = silence_threshold
        self.pause_threshold = pause_threshold
        
        # State tracking
        self.is_speaking = False
        self.silence_start_time = None
        self.last_speech_time = time.time()
        
        # Callbacks
        self.on_speech_start: Optional[Callable] = None
        self.on_speech_end: Optional[Callable] = None
        self.on_pause_detected: Optional[Callable[[float], None]] = None
        
    def process_audio_frame(self, audio_data: np.ndarray) -> dict:
        """Process single audio frame and return VAD status"""
        # Calculate RMS energy
        rms_energy = np.sqrt(np.mean(audio_data ** 2))
        
        # Determine if currently speaking
        is_speech = rms_energy > self.silence_threshold
        
        current_time = time.time()
        
        if is_speech:
            if not self.is_speaking:
                # Speech started
                self.is_speaking = True
                self.silence_start_time = None
                if self.on_speech_start:
                    self.on_speech_start()
            
            self.last_speech_time = current_time
            
        else:
            if self.is_speaking:
                # Potential pause/end of speech
                if self.silence_start_time is None:
                    self.silence_start_time = current_time
                
                pause_duration = current_time - self.silence_start_time
                
                if pause_duration >= self.pause_threshold:
                    # Pause threshold reached
                    self.is_speaking = False
                    if self.on_pause_detected:
                        self.on_pause_detected(pause_duration)
                    if self.on_speech_end:
                        self.on_speech_end()
        
        return {
            'is_speech': is_speech,
            'rms_energy': rms_energy,
            'pause_duration': (current_time - self.silence_start_time) if self.silence_start_time else 0,
            'is_speaking': self.is_speaking
        }
```

### Step 2: WebSocket Bridge Integration (1-2 days)
```python
# Modify workshop_websocket_bridge.py
class WorkshopWebSocketBridge:
    def __init__(self):
        # ... existing code ...
        self.vad = VoiceActivityDetector(
            pause_threshold=1.5  # Configurable
        )
        self.vad.on_pause_detected = self.handle_pause_detected
        
    def handle_pause_detected(self, pause_duration: float):
        """Handle automatic commit trigger from VAD"""
        if self.current_text.strip():
            # Trigger commit & continue action
            self.commit_and_continue()
            
    def process_audio_chunk(self, audio_data):
        # ... existing Parakeet processing ...
        
        # Add VAD processing
        vad_status = self.vad.process_audio_frame(audio_data)
        
        # Send VAD status to UI
        self.send_to_clients({
            'type': 'vad_status',
            'data': vad_status
        })
```

### Step 3: UI Integration (2-3 days)
```typescript
// workshop-box-ui/src/components/WorkshopBox.tsx
const WorkshopBox: React.FC = () => {
  const [vadStatus, setVadStatus] = useState<VADStatus>({
    isActive: false,
    audioLevel: 0,
    pauseDuration: 0,
    willCommitIn: 0
  });

  // WebSocket message handling
  useEffect(() => {
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === 'vad_status') {
        setVadStatus(message.data);
      }
    };
  }, []);

  return (
    <div className="workshop-box">
      {/* VAD Status Indicator */}
      <div className="vad-indicator">
        <MicrophoneIcon 
          className={vadStatus.isActive ? 'active' : 'inactive'} 
        />
        <div className="audio-level-bar">
          <div 
            className="level-fill"
            style={{ width: `${vadStatus.audioLevel * 100}%` }}
          />
        </div>
      </div>
      
      {/* Auto-commit countdown */}
      {vadStatus.willCommitIn > 0 && (
        <div className="commit-countdown">
          Auto-commit in {Math.ceil(vadStatus.willCommitIn / 1000)}s
        </div>
      )}
      
      {/* ... existing transcription display ... */}
    </div>
  );
};
```

## Configuration & Testing

### Configuration Options
```python
# Add to config_manager.py
class VADSettings:
    enabled: bool = True
    sensitivity: str = "medium"  # low/medium/high preset
    custom_threshold: Optional[float] = None
    pause_duration_ms: int = 1500
    adaptive_mode: bool = True
    breathing_detection: bool = True
    background_noise_adaptation: bool = True
```

### Testing Strategy
1. **Unit Tests** - Individual VAD component testing
2. **Integration Tests** - Full pipeline with real audio
3. **User Testing** - Various speaking patterns and environments
4. **Performance Testing** - CPU/memory usage with continuous VAD

### Performance Considerations
- **Lightweight processing** - VAD must not impact transcription performance
- **Configurable frame rates** - Balance accuracy vs. CPU usage
- **Memory efficiency** - Circular buffers for audio history
- **Thread safety** - VAD runs in separate thread from main transcription

## Dependencies
```bash
# Additional packages needed
pip install webrtcvad  # Optional: Pre-trained VAD model
pip install scipy      # For advanced signal processing
pip install librosa    # Optional: Spectral analysis features
```

## Success Criteria
1. **Accurate pause detection** - 90%+ accuracy in normal speaking conditions
2. **Low false positives** - <5% false commits during continuous speech
3. **Configurable sensitivity** - Works for different speaking styles
4. **Real-time performance** - <50ms additional latency
5. **Seamless integration** - No disruption to existing transcription quality

## Risk Mitigation
- **Manual override** - Always allow user to disable VAD
- **Fallback modes** - Degrade gracefully if VAD fails
- **Performance monitoring** - Track VAD impact on system performance
- **User feedback** - Easy adjustment of sensitivity settings

This implementation plan provides a complete roadmap for adding intelligent voice activity detection to PersonalParakeet's Workshop Box system.