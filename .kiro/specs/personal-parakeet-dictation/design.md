# Design Document

## BREAKTHROUGH STATUS: PROVEN WORKING ARCHITECTURE ✅

**Validated Components (July 2025):**
- ✅ Direct NeMo integration (no FastAPI service needed)
- ✅ LocalAgreement buffering algorithm functional
- ✅ Real-time audio processing pipeline working
- ✅ Text stabilization preventing rewrites
- ✅ Single-file deployment model proven

## Overview

PersonalParakeet is a real-time dictation system that uses direct NeMo integration with LocalAgreement buffering to deliver superior speech-to-text experience. The proven architecture eliminates the complexity of separate services by integrating NVIDIA Parakeet directly into the client application, while implementing novel LocalAgreement buffering to prevent text rewrites that plague traditional dictation systems.

## Architecture

### Proven System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PersonalParakeet Client                               │
│                              (Single Process)                                   │
├─────────────────┬──────────────────────┬─────────────────────┬─────────────────┤
│   Hotkey        │  LocalAgreement      │  Audio Capture      │  Text Injection │
│   Handler       │  Buffer              │  System             │  Engine         │
│   (F4 Toggle)   │  (Core Innovation)   │  (sounddevice)      │  (keyboard lib) │
└─────────────────┴──────────────────────┴─────────────────────┴─────────────────┘
                           │                        │
                           ▼                        ▼
                  ┌─────────────────┐    ┌─────────────────────┐
                  │ NVIDIA Parakeet │    │  Real-time Audio    │
                  │ Model + NeMo    │    │  Processing         │
                  │ (Direct GPU)    │    │  (16kHz chunks)     │
                  └─────────────────┘    └─────────────────────┘
```

### Component Breakdown

#### 1. Audio Capture System ✅ WORKING
- **Implementation**: `sounddevice` library for Windows audio
- **Responsibility**: Real-time microphone capture and processing
- **Features**: Device detection, 16kHz sampling, chunk-based processing
- **Status**: Proven functional with proper audio levels detected

#### 2. NVIDIA Parakeet Integration ✅ WORKING  
- **Implementation**: Direct NeMo ASR model loading
- **Responsibility**: GPU-accelerated speech transcription
- **Features**: Parakeet-TDT-1.1B model, CUDA acceleration, real-time processing
- **Status**: Successfully transcribing speech with high accuracy

#### 3. LocalAgreement Buffer ✅ WORKING
- **Implementation**: `ESSENTIAL_LocalAgreement_Code.py`
- **Responsibility**: Prevent text rewrites through agreement tracking
- **Key Algorithm**: Track word stability across consecutive transcription updates
- **Status**: Proven functional - text stabilizes instead of constantly rewriting

#### 4. Hotkey System ✅ WORKING
- **Implementation**: `keyboard` library for global hotkeys
- **Responsibility**: F4 toggle for dictation start/stop
- **Features**: Global hotkey detection, system integration
- **Status**: F4 toggle working reliably

#### 5. Text Injection Engine ❌ NEEDS FIXING
- **Implementation**: `keyboard.write()` for text output
- **Responsibility**: Insert committed text into active applications
- **Current Issue**: Callback errors preventing actual text output
- **Status**: Core logic works, output mechanism needs debugging

## Components and Interfaces

### LocalAgreement Buffer System

```python
class TranscriptionProcessor:
    def __init__(self, agreement_threshold: int = 2, enable_visual_feedback: bool = True)
    
    # Core Methods
    def process_transcription(self, raw_transcription: str) -> TextState
    def set_text_output_callback(self, callback: Callable[[str], None]) -> None
    def get_display_text(self) -> Tuple[str, str]
    
    # Configuration
    def set_agreement_threshold(self, threshold: int) -> None
    def set_timeout_seconds(self, timeout: float) -> None
    
    # Callbacks
    on_committed_text: Optional[Callable[[str], None]]
    on_state_update: Optional[Callable[[TextState], None]]

class LocalAgreementBuffer:
    def __init__(self, agreement_threshold: int = 2, max_pending_words: int = 20)
    
    # Core State
    committed_text: str
    pending_words: List[str]
    word_agreements: Dict[int, Dict[str, int]]  # position -> word -> count
    
    # Core Methods
    def update_transcription(self, new_transcription: str) -> TextState
    def get_current_state(self) -> TextState
    def _check_agreements(self) -> List[str]
    def _cleanup_old_agreements(self) -> None
```

### Audio Capture System

```python
class SimpleDictation:
    def __init__(self):
        # Audio Configuration
        self.sample_rate: int = 16000
        self.chunk_duration: float = 2.0
        self.chunk_size: int
        
        # State Management
        self.is_recording: bool = False
        self.audio_queue: Queue[np.ndarray]
        
        # Core Components
        self.model: nemo_asr.models.ASRModel  # Direct Parakeet model
        self.processor: TranscriptionProcessor  # LocalAgreement
        self.processing_thread: Thread
        self.stream: sd.InputStream
    
    # Device Management
    def list_audio_devices(self) -> List[AudioDevice]
    def select_device(self, device_pattern: str) -> bool
    
    # Core Methods
    def output_text(self, text: str) -> None
    def audio_callback(self, indata: np.ndarray, frames: int, time: Any, status: Any) -> None
    def process_audio_loop(self) -> None
    def start_dictation(self) -> None
    def stop_dictation(self) -> None
    def toggle_dictation(self) -> None
```

### Advanced Voice Activity Detection

```python
class DualVADSystem:
    def __init__(self):
        self.silero_vad: SileroVAD
        self.webrtc_vad: WebRTCVAD
        self.sensitivity_threshold: float = 0.5
        self.pre_roll_seconds: float = 0.5
        self.post_roll_seconds: float = 1.0
    
    # Core VAD Methods
    def detect_speech(self, audio_chunk: np.ndarray) -> VADResult
    def is_speech_detected(self, audio_chunk: np.ndarray) -> bool
    def get_speech_boundaries(self, audio_stream: np.ndarray) -> List[Tuple[float, float]]
    
    # Configuration
    def set_sensitivity(self, threshold: float) -> None
    def adapt_to_environment(self, noise_level: float) -> None
    def configure_buffers(self, pre_roll: float, post_roll: float) -> None

@dataclass
class VADResult:
    is_speech: bool
    confidence: float
    silero_score: float
    webrtc_score: float
    timestamp: float
```

### Text Injection Engine

```python
class TextInjectionEngine:
    def __init__(self):
        self.application_detector: ApplicationDetector
        self.injection_strategies: Dict[ApplicationType, InjectionStrategy]
        self.fallback_overlay: OverlayDisplay
    
    # Application Detection
    def get_active_application(self) -> ApplicationInfo
    def detect_injection_strategy(self, app_info: ApplicationInfo) -> InjectionStrategy
    def classify_application_type(self, process_name: str, window_title: str) -> ApplicationType
    
    # Text Injection
    async def inject_text(self, text: str, strategy: InjectionStrategy) -> bool
    def track_injection_state(self, text: str) -> None
    
    # Strategies
    def paste_strategy(self, text: str) -> bool  # For editors
    def type_strategy(self, text: str) -> bool   # For browsers
    def overlay_strategy(self, text: str) -> bool # Fallback

class ApplicationDetector:
    def __init__(self):
        self.editor_patterns: List[str] = ["code", "notepad", "sublime", "vim", "emacs"]
        self.browser_patterns: List[str] = ["chrome", "firefox", "edge", "safari"]
        self.terminal_patterns: List[str] = ["cmd", "powershell", "terminal", "bash"]
    
    def detect_active_window(self) -> ApplicationInfo
    def classify_by_process_name(self, process_name: str) -> ApplicationType
    def classify_by_window_title(self, window_title: str) -> ApplicationType
    def get_injection_capabilities(self, app_info: ApplicationInfo) -> InjectionCapabilities

@dataclass
class InjectionCapabilities:
    supports_paste: bool
    supports_typing: bool
    supports_clipboard: bool
    requires_focus: bool
    injection_delay_ms: int
```

### Dictation Client (Main Orchestrator)

```python
class PersonalParakeetClient:
    def __init__(self, config: DictationConfig)
    
    # System Lifecycle
    async def initialize(self) -> None
    async def start_dictation(self) -> None
    async def stop_dictation(self) -> None
    async def shutdown(self) -> None
    
    # Hotkey Handlers
    def on_f4_pressed(self) -> None  # Toggle dictation
    def on_f5_pressed(self) -> None  # LLM refinement
    def on_ctrl_alt_q(self) -> None  # Quit
    
    # Status Management
    def update_status_display(self, status: SystemStatus) -> None
    def show_error_message(self, error: str) -> None
```

## Data Models

### Core Data Structures

```python
@dataclass
class TextState:
    """Represents current LocalAgreement buffer state"""
    committed: str = ""
    pending: str = ""
    full_text: str = ""
    newly_committed: str = ""
    confidence_score: float = 0.0
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class AudioDevice:
    """Audio input device information"""
    id: int
    name: str
    channels: int
    sample_rate: int
    is_default: bool

@dataclass
class ApplicationInfo:
    """Active application context"""
    window_title: str
    process_name: str
    application_type: ApplicationType  # EDITOR, BROWSER, TERMINAL, UNKNOWN
    supports_paste: bool
    supports_typing: bool

@dataclass
class SystemStatus:
    """Overall system state"""
    is_dictating: bool
    is_processing: bool
    audio_level: float
    gpu_utilization: float
    error_message: Optional[str]
    last_transcription: Optional[str]

@dataclass
class DictationConfig:
    """System configuration"""
    agreement_threshold: int = 2
    audio_device_pattern: str = ""
    hotkeys: Dict[str, str] = field(default_factory=dict)
    llm_provider: str = "ollama"
    ui_mode: str = "overlay"  # overlay, tray, hidden

@dataclass
class AudioConfig:
    """Audio system configuration"""
    sample_rate: int = 16000
    chunk_duration: float = 2.0
    channels: int = 1
    device_id: Optional[int] = None
    silence_threshold: float = 0.01

@dataclass
class ModelConfig:
    """NeMo model configuration"""
    model_name: str = "nvidia/parakeet-tdt-1.1b"
    device: str = "cuda"
    dtype: torch.dtype = torch.float16
    batch_size: int = 1

@dataclass
class LocalAgreementConfig:
    """LocalAgreement algorithm configuration"""
    agreement_threshold: int = 2
    max_pending_words: int = 20
    word_timeout_seconds: float = 5.0
    position_tolerance: int = 2

@dataclass
class SystemConfig:
    """Overall system configuration"""
    audio: AudioConfig = field(default_factory=AudioConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    agreement: LocalAgreementConfig = field(default_factory=LocalAgreementConfig)
    hotkeys: Dict[str, str] = field(default_factory=lambda: {"toggle": "f4"})
```

### Configuration Schema (TOML)

```toml
[audio]
device_pattern = "Blue Yeti"
sample_rate = 16000
chunk_duration = 2.0
channels = 1
silence_threshold = 0.01

[model]
name = "nvidia/parakeet-tdt-1.1b"
device = "cuda"
precision = "fp16"
batch_size = 1

[agreement]
threshold = 2
max_pending_words = 20
word_timeout_seconds = 5.0
position_tolerance = 2

[text_injection]
default_strategy = "auto"
paste_applications = ["code", "notepad", "sublime"]
type_applications = ["chrome", "firefox", "edge"]

[hotkeys]
toggle_dictation = "F4"
llm_refinement = "F5"
context_enhancement = "F1+F4"
quit_application = "Ctrl+Alt+Q"

[llm]
provider = "ollama"
model = "llama3"
api_key = ""
timeout_seconds = 5

[ui]
mode = "overlay"
show_pending_text = true
transparency = 0.8
position = "top-right"

[gpu]
primary_device = 0
secondary_device = 1
memory_fraction = 0.85

[debug]
show_audio_levels = true
show_transcription_raw = true
show_agreement_state = true
log_to_file = false
```

## Error Handling

### Error Categories and Strategies

#### 1. Audio System Errors
- **Device Not Found**: Graceful fallback to default device with user notification
- **Permission Denied**: Clear instructions for enabling microphone access
- **Audio Stream Failure**: Automatic reconnection with exponential backoff

#### 2. Model Loading and Transcription Errors
- **Model Loading Failure**: Retry with progress indicator, fallback to CPU if needed
- **CUDA Out of Memory**: Reduce batch size, use FP16 precision, notify user
- **Transcription Timeout**: Skip chunk, continue processing, log performance warning

#### 3. Text Injection Errors
- **Application Not Responding**: Fallback to overlay display
- **Injection Failure**: Retry with alternative strategy
- **Permission Issues**: Provide troubleshooting guidance

#### 4. LocalAgreement Buffer Errors
- **Memory Overflow**: Automatic buffer cleanup with state preservation
- **Agreement Timeout**: Force commit pending text with user notification
- **State Corruption**: Reset buffer with minimal data loss

### GPU Management System

```python
class GPUManager:
    def __init__(self):
        self.available_gpus: List[GPUInfo] = []
        self.parakeet_gpu: Optional[int] = None
        self.llm_gpu: Optional[int] = None
    
    # GPU Detection and Allocation
    def detect_gpus(self) -> List[GPUInfo]
    def allocate_optimal_gpus(self) -> GPUAllocation
    def get_gpu_memory_info(self, gpu_id: int) -> GPUMemoryInfo
    
    # Resource Management
    def monitor_gpu_usage(self) -> Dict[int, float]
    def handle_memory_pressure(self, gpu_id: int) -> bool
    def reallocate_if_needed(self) -> bool

@dataclass
class GPUInfo:
    id: int
    name: str
    memory_total: int
    memory_free: int
    compute_capability: Tuple[int, int]
    is_rtx_5090: bool
    is_rtx_3090: bool

@dataclass
class GPUAllocation:
    parakeet_gpu: int
    llm_gpu: int
    shared_mode: bool
    memory_split: Optional[float]
```

### Error Recovery Patterns

```python
class ErrorRecoveryManager:
    async def handle_audio_error(self, error: AudioError) -> RecoveryAction
    async def handle_model_error(self, error: ModelError) -> RecoveryAction
    async def handle_injection_error(self, error: InjectionError) -> RecoveryAction
    async def handle_gpu_error(self, error: GPUError) -> RecoveryAction
    
    def log_error_with_context(self, error: Exception, context: Dict) -> None
    def notify_user(self, message: str, severity: ErrorSeverity) -> None
    def attempt_recovery(self, recovery_action: RecoveryAction) -> bool
```

## Testing Strategy

### Unit Testing
- **LocalAgreement Algorithm**: Test agreement tracking, timeout handling, edge cases
- **Audio Processing**: Mock audio streams, device detection, format conversion
- **Text Injection**: Mock applications, strategy selection, injection tracking
- **Configuration**: Validation, defaults, error handling

### Integration Testing
- **Model Integration**: Direct NeMo model loading, GPU allocation, inference pipeline
- **End-to-End Flow**: Audio capture → transcription → agreement → injection
- **Error Scenarios**: Model failures, GPU memory issues, audio device constraints

### Performance Testing
- **Latency Measurement**: Audio capture to text injection timing
- **Memory Usage**: Long-running sessions, buffer management
- **GPU Utilization**: Transcription performance under load
- **Concurrent Operations**: Multiple audio streams, background processing

### User Acceptance Testing
- **Dictation Accuracy**: Compare against baseline systems
- **LocalAgreement Effectiveness**: Measure text rewrite reduction
- **Hotkey Responsiveness**: Timing and reliability
- **Application Compatibility**: Test across target applications

## Implementation Phases

### Phase 1: Core LocalAgreement System (Days 1-5)
- Implement LocalAgreement buffering algorithm
- Direct NeMo model integration and loading
- Basic text state management and callbacks
- Unit tests for agreement logic

### Phase 2: Audio Integration (Days 6-10)
- Audio device detection and selection
- Real-time capture and direct processing
- Audio chunk processing with model inference
- VAD integration and configuration

### Phase 3: Text Injection System (Days 11-15)
- Application detection and classification
- Injection strategy implementation
- Clipboard and typing simulation
- Fallback overlay system

### Phase 4: Dictation Client UI (Days 16-20)
- Hotkey system implementation
- Status display and user feedback
- Configuration management
- Error handling and recovery

### Phase 5: Integration and Polish (Days 21-25)
- End-to-end testing and debugging
- Performance optimization
- Documentation and deployment
- User acceptance validation

## Deployment Architecture

### Development Setup
```bash
# Setup Python 3.11 environment
uv venv --python 3.11 .venv
.venv\Scripts\activate

# Install dependencies
pip install nemo-toolkit[asr]
pip install sounddevice numpy keyboard

# Run dictation system
python dictation_simple.py
```

### Production Deployment
- **Single Executable**: Standalone executable with embedded dependencies (PyInstaller)
- **Configuration**: User-specific TOML files in `%APPDATA%/PersonalParakeet/`
- **Model Cache**: Local Parakeet model cache for offline operation
- **Logging**: Structured logs for troubleshooting and performance monitoring

This design uses direct NeMo integration to implement the core LocalAgreement innovation and real-time dictation experience that makes PersonalParakeet unique.