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

### Platform-Aware Text Injection Engine

```python
class PlatformAwareTextInjectionEngine:
    def __init__(self):
        self.platform = self._detect_platform()
        self.application_detector: ApplicationDetector
        self.injection_strategies: Dict[ApplicationType, InjectionStrategy]
        self.fallback_overlay: OverlayDisplay
        
        # Platform-specific injectors
        self.windows_injector: Optional[WindowsInjector] = None
        self.kde_injector: Optional[KDEPlasmaInjector] = None
        self.gnome_injector: Optional[GNOMEInjector] = None
        self._initialize_platform_injector()
    
    # Platform Detection
    def _detect_platform(self) -> PlatformInfo:
        """Detect OS and desktop environment"""
        platform_info = PlatformInfo()
        platform_info.os = platform.system()
        
        if platform_info.os == "Linux":
            # Detect desktop environment
            desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
            if 'kde' in desktop:
                platform_info.desktop_env = 'KDE'
                platform_info.session_type = os.environ.get('XDG_SESSION_TYPE', 'x11')
            elif 'gnome' in desktop:
                platform_info.desktop_env = 'GNOME'
                platform_info.session_type = os.environ.get('XDG_SESSION_TYPE', 'x11')
        return platform_info
    
    # Application Detection
    def get_active_application(self) -> ApplicationInfo
    def detect_injection_strategy(self, app_info: ApplicationInfo) -> InjectionStrategy
    def classify_application_type(self, process_name: str, window_title: str) -> ApplicationType
    
    # Text Injection
    async def inject_text(self, text: str, strategy: Optional[InjectionStrategy] = None) -> bool:
        """Main injection method with platform-aware routing"""
        if not strategy:
            app_info = self.get_active_application()
            strategy = self.detect_injection_strategy(app_info)
        
        try:
            if self.platform.os == "Windows":
                return await self.windows_injector.inject(text, strategy)
            elif self.platform.os == "Linux":
                if self.platform.desktop_env == "KDE":
                    return await self.kde_injector.inject(text, strategy)
                elif self.platform.desktop_env == "GNOME":
                    return await self.gnome_injector.inject(text, strategy)
        except Exception as e:
            logger.error(f"Injection failed: {e}")
            return await self._fallback_injection(text)
    
    async def _fallback_injection(self, text: str) -> bool:
        """Try alternative methods when primary fails"""
        methods = self._get_fallback_methods()
        for method in methods:
            try:
                if await method(text):
                    return True
            except:
                continue
        return self.overlay_strategy(text)

class WindowsInjector:
    """Windows-specific text injection implementation with UI Automation"""
    def __init__(self):
        import keyboard  # Windows keyboard library
        self.keyboard = keyboard
        self.uia = None
        self._init_ui_automation()
        
    def _init_ui_automation(self):
        """Initialize Windows UI Automation for smart injection"""
        try:
            import comtypes.client
            from comtypes import automation
            # Create UI Automation instance
            self.uia = comtypes.client.CreateObject(
                "{ff48dba4-60ef-4201-aa87-54103eef594e}",
                interface=automation.IUIAutomation
            )
        except:
            # UI Automation not available, will fallback to keyboard
            self.uia = None
    
    async def inject(self, text: str, strategy: InjectionStrategy) -> bool:
        # Try UI Automation first (most reliable)
        if self.uia and self._inject_via_ui_automation(text):
            return True
            
        # Fallback to strategy-based injection
        if strategy == InjectionStrategy.PASTE:
            return self._inject_via_clipboard(text)
        elif strategy == InjectionStrategy.TYPE:
            return self._inject_via_typing(text)
        else:
            return self._inject_direct(text)
    
    def _inject_via_ui_automation(self, text: str) -> bool:
        """Smart text injection using UI Automation (like Win+H)"""
        try:
            # Get the currently focused element
            focused = self.uia.GetFocusedElement()
            
            # Try to get text pattern (most reliable for text fields)
            UIA_TextPatternId = 10014
            UIA_ValuePatternId = 10002
            
            # First try TextPattern (for rich text controls)
            try:
                text_pattern = focused.GetCurrentPattern(UIA_TextPatternId)
                if text_pattern:
                    # Insert text at current position
                    text_pattern.DocumentRange.InsertText(text + " ")
                    return True
            except:
                pass
            
            # Try ValuePattern (for simple text inputs)
            try:
                value_pattern = focused.GetCurrentPattern(UIA_ValuePatternId)
                if value_pattern:
                    # Get current value and append
                    current = value_pattern.CurrentValue
                    value_pattern.SetValue(current + text + " ")
                    return True
            except:
                pass
                
        except Exception as e:
            # UI Automation failed, will use fallback
            pass
        
        return False
    
    def _inject_direct(self, text: str) -> bool:
        """Direct keyboard.write() - fallback method"""
        try:
            self.keyboard.write(text + " ")
            return True
        except:
            return False
    
    def _inject_via_typing(self, text: str) -> bool:
        """Character-by-character typing for compatibility"""
        try:
            for char in text + " ":
                self.keyboard.press_and_release(char)
                time.sleep(0.01)  # Small delay for compatibility
            return True
        except:
            return False
    
    def _inject_via_clipboard(self, text: str) -> bool:
        """Clipboard paste for editors"""
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
            self.keyboard.press_and_release('ctrl+v')
            return True
        except:
            return False

class KDEPlasmaInjector:
    """KDE Plasma-specific text injection (X11/Wayland)"""
    def __init__(self):
        self.display = None
        self.session_bus = None
        self._init_x11()
        self._init_dbus()
        
    def _init_x11(self):
        """Initialize X11 for XTEST injection"""
        try:
            from Xlib import display, X
            from Xlib.ext import xtest
            self.display = display.Display()
            self.xtest = xtest
            self.X = X
        except:
            pass
    
    def _init_dbus(self):
        """Initialize D-Bus for KDE integration"""
        try:
            import dbus
            self.session_bus = dbus.SessionBus()
        except:
            pass
    
    async def inject(self, text: str, strategy: InjectionStrategy) -> bool:
        # Get active application
        app_class = self._get_active_window_class()
        
        # KDE-specific optimizations
        if app_class == 'konsole' and self.session_bus:
            return self._inject_konsole_dbus(text)
        elif app_class in ['kate', 'kwrite'] and strategy == InjectionStrategy.PASTE:
            return self._inject_via_clipboard(text)
        else:
            # Default to XTEST
            return self._inject_xtest(text)
    
    def _inject_xtest(self, text: str) -> bool:
        """Most reliable method for KDE X11"""
        if not self.display:
            return False
            
        for char in text:
            keycode = self.display.keysym_to_keycode(ord(char))
            self.xtest.fake_input(self.display, self.X.KeyPress, keycode)
            self.xtest.fake_input(self.display, self.X.KeyRelease, keycode)
        self.display.sync()
        return True
    
    def _inject_konsole_dbus(self, text: str) -> bool:
        """Direct D-Bus injection for Konsole"""
        try:
            subprocess.run([
                'qdbus', 'org.kde.konsole', '/konsole/MainWindow_1',
                'org.kde.konsole.Window.sendText', text
            ])
            return True
        except:
            return False

class GNOMEInjector:
    """GNOME-specific text injection (Wayland/X11)"""
    def __init__(self):
        self.at_spi = None
        self._init_at_spi()
        
    def _init_at_spi(self):
        """Initialize AT-SPI for accessibility-based injection"""
        try:
            import pyatspi
            self.at_spi = pyatspi
        except:
            pass
    
    async def inject(self, text: str, strategy: InjectionStrategy) -> bool:
        # Try AT-SPI first for Wayland compatibility
        if self.at_spi and self._inject_at_spi(text):
            return True
        
        # Fallback to xdotool for X11
        return self._inject_xdotool(text)
    
    def _inject_at_spi(self, text: str) -> bool:
        """Use AT-SPI accessibility framework"""
        try:
            # Get focused object
            registry = self.at_spi.Registry()
            desktop = registry.getDesktop(0)
            focused = self._find_focused_text_object(desktop)
            
            if focused:
                focused.set_text_contents(text)
                return True
        except:
            pass
        return False

class ApplicationDetector:
    def __init__(self):
        self.platform = platform.system()
        self.editor_patterns: List[str] = ["code", "notepad", "sublime", "vim", "emacs", "kate", "kwrite"]
        self.browser_patterns: List[str] = ["chrome", "firefox", "edge", "safari"]
        self.terminal_patterns: List[str] = ["cmd", "powershell", "terminal", "bash", "konsole", "gnome-terminal"]
    
    def detect_active_window(self) -> ApplicationInfo:
        """Platform-aware active window detection"""
        if self.platform == "Windows":
            return self._detect_windows()
        elif self.platform == "Linux":
            return self._detect_linux()
        return ApplicationInfo(process_name="unknown", window_title="")
    
    def _detect_windows(self) -> ApplicationInfo:
        """Windows-specific window detection"""
        import win32gui
        import win32process
        
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = self._get_process_name_windows(pid)
        
        return ApplicationInfo(
            process_name=process_name,
            window_title=window_title,
            platform="Windows"
        )
    
    def _detect_linux(self) -> ApplicationInfo:
        """Linux window detection using xdotool"""
        try:
            # Get active window ID
            window_id = subprocess.check_output(['xdotool', 'getactivewindow']).decode().strip()
            
            # Get window class
            window_class = subprocess.check_output([
                'xdotool', 'getwindowclassname', window_id
            ]).decode().strip()
            
            # Get window title
            window_title = subprocess.check_output([
                'xdotool', 'getwindowname', window_id
            ]).decode().strip()
            
            return ApplicationInfo(
                process_name=window_class.lower(),
                window_title=window_title,
                platform="Linux"
            )
        except:
            return ApplicationInfo(process_name="unknown", window_title="")
    
    def classify_by_process_name(self, process_name: str) -> ApplicationType
    def classify_by_window_title(self, window_title: str) -> ApplicationType
    def get_injection_capabilities(self, app_info: ApplicationInfo) -> InjectionCapabilities

@dataclass
class PlatformInfo:
    os: str = ""  # Windows, Linux, Darwin
    desktop_env: str = ""  # KDE, GNOME, etc
    session_type: str = ""  # x11, wayland
    
@dataclass
class InjectionCapabilities:
    supports_paste: bool
    supports_typing: bool
    supports_clipboard: bool
    supports_xtest: bool  # Linux X11
    supports_dbus: bool   # Linux KDE
    supports_at_spi: bool # Linux accessibility
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

## Configuration System Design

### Configuration Profiles Architecture

The configuration system implements a profile-based approach with four pre-tuned profiles optimized for different usage scenarios. Each profile balances the trade-offs between accuracy, responsiveness, and stability.

#### Profile Definitions

```python
@dataclass
class ConfigurationProfile:
    """Pre-defined configuration profile for specific use cases"""
    name: str
    description: str
    agreement_threshold: int        # 1-5: consecutive agreements needed
    chunk_duration: float          # 0.3-2.0s: audio chunk size
    max_pending_words: int         # 5-30: buffer size
    word_timeout: float            # 2.0-7.0s: force commit timeout
    position_tolerance: int        # 1-3: word position flexibility
    audio_level_threshold: float   # 0.001-0.1: minimum audio level

# Pre-defined profiles
FAST_CONVERSATION = ConfigurationProfile(
    name="Fast Conversation Mode",
    description="Optimized for quick responses in conversational settings",
    agreement_threshold=1,      # Immediate commitment
    chunk_duration=0.3,         # Short chunks for speed
    max_pending_words=8,        # Small buffer
    word_timeout=2.0,           # Quick timeout
    position_tolerance=3,       # Flexible matching
    audio_level_threshold=0.005 # Moderate sensitivity
)

BALANCED_MODE = ConfigurationProfile(
    name="Balanced Mode",
    description="Balanced accuracy and responsiveness for general use",
    agreement_threshold=2,      # Standard stability
    chunk_duration=1.0,         # Standard chunks
    max_pending_words=15,       # Moderate buffer
    word_timeout=4.0,           # Balanced timeout
    position_tolerance=2,       # Standard flexibility
    audio_level_threshold=0.01  # Default sensitivity
)

ACCURATE_DOCUMENT = ConfigurationProfile(
    name="Accurate Document Mode", 
    description="Maximizes accuracy for formal document dictation",
    agreement_threshold=3,      # High stability requirement
    chunk_duration=2.0,         # Long chunks for context
    max_pending_words=30,       # Large buffer
    word_timeout=7.0,           # Extended timeout
    position_tolerance=1,       # Strict matching
    audio_level_threshold=0.02  # Reduced sensitivity
)

LOW_LATENCY = ConfigurationProfile(
    name="Low-Latency Mode",
    description="Minimizes delay for real-time applications",
    agreement_threshold=1,      # Immediate commitment
    chunk_duration=0.5,         # Balanced for low latency
    max_pending_words=5,        # Minimal buffer
    word_timeout=2.5,           # Quick timeout
    position_tolerance=2,       # Moderate flexibility
    audio_level_threshold=0.001 # High sensitivity
)
```

#### Configuration Manager

```python
class ConfigurationManager:
    """Manages configuration profiles and runtime settings"""
    
    def __init__(self):
        self.profiles: Dict[str, ConfigurationProfile] = {
            "fast_conversation": FAST_CONVERSATION,
            "balanced": BALANCED_MODE,
            "accurate_document": ACCURATE_DOCUMENT,
            "low_latency": LOW_LATENCY
        }
        self.active_profile: str = "balanced"
        self.custom_profiles: Dict[str, ConfigurationProfile] = {}
        self.config_file_path: Path = Path.home() / ".personalparakeet" / "config.toml"
    
    # Profile Management
    def load_profile(self, profile_name: str) -> ConfigurationProfile
    def save_custom_profile(self, name: str, profile: ConfigurationProfile) -> None
    def delete_custom_profile(self, name: str) -> bool
    def list_available_profiles(self) -> List[str]
    
    # Configuration Application
    def apply_profile(self, profile_name: str) -> None
    def get_active_configuration(self) -> ConfigurationProfile
    def update_parameter(self, param: str, value: Any) -> None
    
    # Validation
    def validate_configuration(self, config: ConfigurationProfile) -> List[str]
    def validate_parameter(self, param: str, value: Any) -> bool
    
    # Persistence
    def load_from_file(self) -> None
    def save_to_file(self) -> None
    def export_profile(self, profile_name: str, file_path: Path) -> None
    def import_profile(self, file_path: Path) -> ConfigurationProfile
```

#### Configuration Integration Points

```python
class SimpleDictation:
    """Enhanced with configuration support"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.config = config_manager.get_active_configuration()
        
        # Apply configuration to components
        self.chunk_duration = self.config.chunk_duration
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # Initialize processor with config
        self.processor = TranscriptionProcessor(
            agreement_threshold=self.config.agreement_threshold,
            max_pending_words=self.config.max_pending_words,
            word_timeout_seconds=self.config.word_timeout,
            position_tolerance=self.config.position_tolerance
        )
        
        # Audio level threshold
        self.audio_level_threshold = self.config.audio_level_threshold
    
    def switch_profile(self, profile_name: str) -> None:
        """Switch configuration profile at runtime"""
        self.config_manager.apply_profile(profile_name)
        self.config = self.config_manager.get_active_configuration()
        self._apply_configuration_changes()
    
    def _apply_configuration_changes(self) -> None:
        """Apply configuration changes without restart"""
        # Update chunk processing
        self.chunk_duration = self.config.chunk_duration
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # Update processor settings
        self.processor.set_agreement_threshold(self.config.agreement_threshold)
        self.processor.set_max_pending_words(self.config.max_pending_words)
        self.processor.set_timeout_seconds(self.config.word_timeout)
        self.processor.set_position_tolerance(self.config.position_tolerance)
        
        # Update audio threshold
        self.audio_level_threshold = self.config.audio_level_threshold
```

#### Configuration UI Integration

```python
class ConfigurationUI:
    """Visual configuration interface"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.profile_selector: ProfileSelector
        self.parameter_sliders: Dict[str, ParameterSlider]
        self.trade_off_visualizer: TradeOffVisualizer
    
    def show_profile_selector(self) -> None:
        """Display profile selection dropdown"""
        profiles = self.config_manager.list_available_profiles()
        # Show UI with profile options
    
    def show_parameter_controls(self) -> None:
        """Display individual parameter sliders"""
        config = self.config_manager.get_active_configuration()
        # Create sliders for each parameter with validation
    
    def visualize_trade_offs(self) -> None:
        """Show accuracy vs responsiveness visualization"""
        # Display radar chart or similar showing:
        # - Accuracy score (based on agreement_threshold, chunk_duration)
        # - Responsiveness score (based on word_timeout, max_pending_words)
        # - Stability score (based on position_tolerance)
        # - Sensitivity score (based on audio_level_threshold)
```

#### Configuration File Format

```toml
[active_profile]
name = "balanced"

[profiles.custom.meeting_notes]
description = "Optimized for meeting transcription"
agreement_threshold = 2
chunk_duration = 1.5
max_pending_words = 20
word_timeout = 5.0
position_tolerance = 2
audio_level_threshold = 0.008

[parameter_ranges]
agreement_threshold = { min = 1, max = 5 }
chunk_duration = { min = 0.3, max = 2.0 }
max_pending_words = { min = 5, max = 30 }
word_timeout = { min = 2.0, max = 7.0 }
position_tolerance = { min = 1, max = 3 }
audio_level_threshold = { min = 0.001, max = 0.1 }

[ui_preferences]
show_trade_off_visualization = true
auto_save_custom_profiles = true
profile_quick_switch_hotkeys = true
```

### Configuration System Benefits

1. **User-Friendly**: Pre-tuned profiles eliminate guesswork for common scenarios
2. **Flexible**: Custom profiles allow power users to fine-tune for specific needs
3. **Runtime Switching**: Change profiles without restarting the application
4. **Visual Feedback**: Trade-off visualization helps users understand impact of changes
5. **Validation**: Parameter ranges prevent invalid configurations
6. **Persistence**: Settings preserved across sessions with TOML storage

## Advanced Dynamic Configuration System

### Dynamic Configuration Extension

The configuration system can be extended with dynamic tuning capabilities that automatically adjust settings based on performance metrics and user behavior patterns.

#### DynamicTuner Class Design
```python
class DynamicTuner:
    """Monitors system performance and adjusts configuration dynamically."""
    
    def __init__(self, config_manager, metrics_store):
        self.config = config_manager
        self.metrics = metrics_store
        self.learning_rate = 0.1
        self.adjustment_interval = 30  # seconds
        
    def monitor_and_adjust(self):
        """Main tuning loop - runs in background thread."""
        # Collect performance metrics
        metrics = self.metrics.get_recent_window()
        
        # Analyze patterns
        adjustments = self.analyze_performance(metrics)
        
        # Apply gradual adjustments
        self.apply_adjustments(adjustments)
        
    def analyze_performance(self, metrics):
        """Determine needed adjustments based on metrics."""
        adjustments = {}
        
        # Rewrite frequency analysis
        if metrics.rewrite_rate > 0.3:  # Too many rewrites
            adjustments['agreement_threshold'] = +0.05
        elif metrics.rewrite_rate < 0.1:  # Too conservative
            adjustments['agreement_threshold'] = -0.05
            
        # Latency analysis
        if metrics.avg_latency > 500:  # Too slow
            adjustments['chunk_duration'] = -0.1
        elif metrics.avg_latency < 200:  # Room for improvement
            adjustments['chunk_duration'] = +0.1
            
        # Speech pattern analysis
        if metrics.pause_variance > threshold:
            adjustments['vad_sensitivity'] = self.calculate_vad_adjustment()
            
        return adjustments
```

#### ApplicationDetector Class Design
```python
class ApplicationDetector:
    """Detects active application and switches profiles automatically."""
    
    def __init__(self, profile_manager):
        self.profiles = profile_manager
        self.app_mappings = {
            'code.exe': 'coding',
            'devenv.exe': 'coding',
            'winword.exe': 'writing',
            'chrome.exe': 'browsing',
            'slack.exe': 'messaging'
        }
        
    def get_active_application(self):
        """Get currently focused application."""
        import win32gui
        import win32process
        
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        # Get process name from PID
        return self.get_process_name(pid)
        
    def auto_switch_profile(self):
        """Switch profile based on active application."""
        app = self.get_active_application()
        
        if app in self.app_mappings:
            profile = self.app_mappings[app]
            self.profiles.switch_to(profile)
            
    def register_custom_mapping(self, app_name, profile):
        """Allow users to define custom app-profile mappings."""
        self.app_mappings[app_name] = profile
        self.save_mappings()
```

#### UserPreferenceTracker Class Design
```python
class UserPreferenceTracker:
    """Learns from user behavior and corrections."""
    
    def __init__(self, storage_path):
        self.storage = storage_path
        self.correction_history = []
        self.profile_switches = []
        self.preference_model = self.load_or_create_model()
        
    def track_correction(self, original, corrected, context):
        """Record when user corrects output."""
        correction = {
            'timestamp': time.time(),
            'original': original,
            'corrected': corrected,
            'context': context,
            'active_profile': self.current_profile,
            'metrics': self.current_metrics
        }
        self.correction_history.append(correction)
        self.update_model(correction)
        
    def track_profile_switch(self, from_profile, to_profile, context):
        """Record manual profile switches."""
        switch = {
            'timestamp': time.time(),
            'from': from_profile,
            'to': to_profile,
            'app': context['active_app'],
            'metrics': context['current_metrics']
        }
        self.profile_switches.append(switch)
        
    def suggest_adjustments(self):
        """Suggest configuration changes based on learned patterns."""
        # Analyze correction patterns
        common_corrections = self.analyze_corrections()
        
        # Analyze profile switching patterns
        profile_patterns = self.analyze_profile_switches()
        
        # Generate suggestions
        suggestions = []
        
        if common_corrections['punctuation_errors'] > threshold:
            suggestions.append({
                'type': 'punctuation_model',
                'action': 'enable_enhanced_punctuation'
            })
            
        if profile_patterns['frequent_manual_switches']:
            suggestions.append({
                'type': 'auto_profile',
                'action': 'update_app_mappings',
                'data': profile_patterns['suggested_mappings']
            })
            
        return suggestions
```

#### PerformanceMonitor Class Design
```python
class PerformanceMonitor:
    """Tracks system performance metrics for optimization."""
    
    def __init__(self, metrics_store):
        self.store = metrics_store
        self.metrics_window = deque(maxlen=1000)
        self.alert_thresholds = {
            'latency': 1000,  # ms
            'accuracy': 0.7,   # minimum accuracy
            'gpu_usage': 90,   # percentage
            'memory': 4096     # MB
        }
        
    def record_transcription(self, audio_timestamp, text_timestamp, text, rewrites):
        """Record metrics for each transcription."""
        metric = {
            'timestamp': time.time(),
            'latency': (text_timestamp - audio_timestamp) * 1000,
            'text_length': len(text),
            'rewrite_count': rewrites,
            'gpu_usage': self.get_gpu_usage(),
            'memory_usage': self.get_memory_usage()
        }
        self.metrics_window.append(metric)
        self.check_alerts(metric)
        
    def get_optimization_suggestions(self):
        """Analyze metrics and suggest optimizations."""
        recent_metrics = list(self.metrics_window)[-100:]
        
        avg_latency = np.mean([m['latency'] for m in recent_metrics])
        rewrite_rate = np.mean([m['rewrite_count'] > 0 for m in recent_metrics])
        
        suggestions = []
        
        if avg_latency > 500:
            suggestions.append({
                'issue': 'high_latency',
                'suggestion': 'reduce_chunk_duration',
                'severity': 'medium'
            })
            
        if rewrite_rate > 0.4:
            suggestions.append({
                'issue': 'excessive_rewrites',
                'suggestion': 'increase_agreement_threshold',
                'severity': 'high'
            })
            
        return suggestions
        
    def export_metrics(self, filepath):
        """Export metrics for analysis."""
        import pandas as pd
        df = pd.DataFrame(list(self.metrics_window))
        df.to_csv(filepath, index=False)
```

### Integration Architecture

```
┌─────────────────────┐
│   Main Dictation    │
│      System         │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│  ConfigurationMgr   │◄────┐
│  (Static + Dynamic) │     │
└──────────┬──────────┘     │
           │                │
    ┌──────┴──────┐         │
    │             │         │
┌───▼───┐    ┌───▼───┐     │
│Dynamic│    │ App   │     │
│ Tuner │    │Detect │     │
└───┬───┘    └───┬───┘     │
    │            │         │
    └────────────┴─────────┤
                           │
┌──────────────────────────▼─┐
│   Performance Monitor      │
│   & Preference Tracker     │
└────────────────────────────┘
```

## Threading Model

- **Main Thread**: UI and control logic
- **Audio Thread**: Audio capture callback
- **Transcription Thread**: Model inference
- **Output Thread**: Keyboard events
- **Monitor Thread**: Performance tracking
- **Tuner Thread**: Dynamic adjustments

## Data Flow

1. **Audio Input** → Audio Capture → Ring Buffer
2. **Ring Buffer** → Transcription Engine → Raw Text
3. **Raw Text** → LocalAgreement → Stabilized Text
4. **Stabilized Text** → Output Manager → Keyboard Events
5. **All Components** → Performance Monitor → Metrics
6. **Metrics** → Dynamic Tuner → Configuration Updates