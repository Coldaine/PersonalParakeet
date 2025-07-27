# PersonalParakeet v3 - Technical Reference

Comprehensive technical documentation for PersonalParakeet v3 components, patterns, and platform-specific implementations.

---

## Component Specifications

### Clarity Engine

**Purpose**: Real-time text correction system that fixes common STT errors including homophones, technical jargon, and contextual mistakes with sub-150ms latency.

#### Architecture
```python
class ClarityEngine:
    def __init__(self):
        self.correction_rules = self._load_correction_rules()
        self.homophone_map = self._load_homophones()
        self.technical_terms = self._load_technical_terms()
        self.context_buffer = deque(maxlen=5)
        
    def correct_text(self, raw_text: str) -> CorrectionResult:
        """Apply corrections with tracking"""
        corrections = []
        corrected = raw_text
        
        # Apply rule-based corrections
        for pattern, replacement in self.correction_rules:
            if pattern.search(corrected):
                before = corrected
                corrected = pattern.sub(replacement, corrected)
                corrections.append(Correction(
                    original=before,
                    corrected=corrected,
                    rule=pattern.pattern,
                    confidence=1.0
                ))
        
        return CorrectionResult(
            original=raw_text,
            corrected=corrected,
            corrections=corrections,
            processing_time=time.time() - start_time
        )
```

#### Correction Rules
- **Homophones**: `too/to`, `your/you're`, `there/their/they're`
- **Technical Terms**: `clod code` → `claude code`, `get hub` → `github`
- **Programming**: `pie torch` → `pytorch`, `dock her` → `docker`
- **Context-Aware**: `colonel` → `kernel` (in tech contexts)

#### Performance
- **Latency**: <50ms average
- **Memory**: <100MB
- **Accuracy**: 95%+ on common corrections

### STT Processor

**Purpose**: Real-time speech-to-text using NVIDIA Parakeet-TDT 1.1B model with intelligent fallback.

#### Factory Pattern
```python
class STTFactory:
    @staticmethod
    def create_processor(config: AppConfig) -> BaseSTTProcessor:
        """Create appropriate STT processor based on system capabilities"""
        
        # Check for forced mock mode
        if config.audio.use_mock_stt:
            return MockSTTProcessor()
            
        # Try to load real STT
        try:
            from core.cuda_compatibility import check_cuda_compatibility
            cuda_available = check_cuda_compatibility()
            
            if cuda_available and config.audio.stt_device == "cuda":
                return RealSTTProcessor(device="cuda")
            else:
                return RealSTTProcessor(device="cpu")
                
        except ImportError as e:
            logger.warning(f"NeMo not available: {e}")
            return MockSTTProcessor()
        except Exception as e:
            logger.error(f"STT initialization failed: {e}")
            return MockSTTProcessor()
```

#### GPU Optimization (RTX 5090)
```python
def load_parakeet_model():
    """Load Parakeet-TDT-1.1B with RTX 5090 compatibility"""
    
    # CUDA compatibility check
    from core.cuda_compatibility import ensure_cuda_compatible
    ensure_cuda_compatible()
    
    # Load with optimizations
    model = nemo_asr.models.ASRModel.from_pretrained(
        "nvidia/parakeet-tdt-1.1b",
        map_location="cuda"
    ).to(dtype=torch.float16)  # FP16 for memory efficiency
    
    # Optimize for inference
    model.eval()
    torch.backends.cudnn.benchmark = True
    
    return model

def transcribe_chunk(model, audio_chunk: np.ndarray) -> str:
    """Transcribe with error handling and optimization"""
    try:
        with torch.inference_mode():
            result = model.transcribe([audio_chunk])
            return result[0].text if result and result[0].text else ""
    except torch.cuda.OutOfMemoryError:
        logger.error("GPU OOM - clearing cache")
        torch.cuda.empty_cache()
        return ""
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return ""
```

### VAD Engine

**Purpose**: Voice activity detection with intelligent pause detection for natural dictation flow.

#### Core Algorithm
```python
class VADEngine:
    def __init__(self, threshold=0.01, pause_duration_ms=1500):
        self.threshold = threshold
        self.pause_duration = pause_duration_ms / 1000.0
        self.last_voice_time = 0
        self.is_speaking = False
        
    def process_audio(self, audio_chunk: np.ndarray) -> VADResult:
        """Process audio chunk and detect voice activity"""
        
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        current_time = time.time()
        
        # Voice activity detection
        voice_detected = rms > self.threshold
        
        if voice_detected:
            self.last_voice_time = current_time
            if not self.is_speaking:
                # Speech started
                self.is_speaking = True
                return VADResult(
                    voice_detected=True,
                    speech_started=True,
                    speech_ended=False,
                    pause_detected=False,
                    rms_level=rms
                )
        else:
            # Check for pause
            silence_duration = current_time - self.last_voice_time
            if self.is_speaking and silence_duration > self.pause_duration:
                # Natural pause detected
                self.is_speaking = False
                return VADResult(
                    voice_detected=False,
                    speech_started=False,
                    speech_ended=True,
                    pause_detected=True,
                    silence_duration=silence_duration,
                    rms_level=rms
                )
        
        return VADResult(
            voice_detected=voice_detected,
            speech_started=False,
            speech_ended=False,
            pause_detected=False,
            rms_level=rms
        )
```

### Text Injection Manager

**Purpose**: Multi-strategy text injection with automatic fallback and performance monitoring.

#### Strategy Pattern
```python
class InjectionManager:
    def __init__(self):
        self.strategies = [
            UIAutomationStrategy(),     # Windows UI Automation (most reliable)
            Win32SendInputStrategy(),   # Direct Windows API
            KeyboardStrategy(),         # Cross-platform keyboard
            ClipboardStrategy(),        # Clipboard fallback
        ]
        self.performance_stats = defaultdict(lambda: {"success": 0, "failure": 0, "avg_time": 0})
        
    async def inject_text(self, text: str, app_info: Optional[AppInfo] = None) -> InjectionResult:
        """Inject text using best available strategy"""
        
        # Get optimized strategy order for this application
        strategy_order = self._get_optimized_strategies(app_info)
        
        for strategy in strategy_order:
            start_time = time.time()
            try:
                success = await strategy.inject(text, app_info)
                duration = time.time() - start_time
                
                if success:
                    self._update_stats(strategy, True, duration)
                    return InjectionResult(
                        success=True,
                        strategy=strategy.__class__.__name__,
                        duration=duration,
                        text=text
                    )
                else:
                    self._update_stats(strategy, False, duration)
                    
            except Exception as e:
                logger.warning(f"Strategy {strategy.__class__.__name__} failed: {e}")
                self._update_stats(strategy, False, time.time() - start_time)
                
        # All strategies failed
        return InjectionResult(
            success=False,
            strategy=None,
            duration=0,
            text=text,
            error="All injection strategies failed"
        )
```

#### Windows UI Automation Strategy
```python
class UIAutomationStrategy(InjectionStrategy):
    """Most reliable strategy for Windows applications"""
    
    def __init__(self):
        self.automation = None
        try:
            import uiautomation as auto
            self.automation = auto
        except ImportError:
            logger.warning("UI Automation not available")
            
    async def inject(self, text: str, app_info: Optional[AppInfo] = None) -> bool:
        if not self.automation:
            return False
            
        try:
            # Get focused element
            focused = self.automation.GetFocusedControl()
            
            if focused and hasattr(focused, 'SendKeys'):
                focused.SendKeys(text)
                return True
            elif focused and hasattr(focused, 'SetValue'):
                current_value = focused.GetValuePattern().Value
                focused.GetValuePattern().SetValue(current_value + text)
                return True
                
        except Exception as e:
            logger.debug(f"UI Automation failed: {e}")
            
        return False
```

---

## Code Patterns Library

### Threading Patterns

#### Producer-Consumer Audio Pipeline
```python
class AudioEngine:
    def __init__(self):
        self.audio_queue = queue.Queue(maxsize=50)
        self.running = False
        self.stt_thread = None
        
    def audio_callback(self, indata, frames, time, status):
        """Producer - runs in sounddevice thread"""
        if status:
            logger.warning(f"Audio callback status: {status}")
        
        try:
            self.audio_queue.put_nowait(indata.copy())
        except queue.Full:
            logger.warning("Audio queue overflow - dropping frame")
            
    def stt_worker(self, page: ft.Page):
        """Consumer - runs in dedicated thread"""
        while self.running:
            try:
                audio_chunk = self.audio_queue.get(timeout=1.0)
                
                # Process chunk
                text = self.stt_processor.transcribe(audio_chunk)
                if text.strip():
                    # Thread-safe UI update
                    asyncio.run_coroutine_threadsafe(
                        self.update_ui(text), 
                        page.loop
                    )
                    
                self.audio_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"STT worker error: {e}")
                
    async def update_ui(self, text: str):
        """UI update must run in main thread"""
        await self.dictation_view.update_transcript(text)
```

#### Thread-Safe Configuration Updates
```python
class ConfigManager:
    def __init__(self):
        self.config = AppConfig()
        self.config_lock = threading.RLock()
        self.change_listeners = []
        
    def update_config(self, updates: dict) -> bool:
        """Thread-safe configuration update"""
        with self.config_lock:
            try:
                # Validate updates
                for key, value in updates.items():
                    if not hasattr(self.config, key):
                        raise ValueError(f"Unknown config key: {key}")
                        
                # Apply updates
                old_config = copy.deepcopy(self.config)
                for key, value in updates.items():
                    setattr(self.config, key, value)
                    
                # Notify listeners
                for listener in self.change_listeners:
                    try:
                        listener(old_config, self.config)
                    except Exception as e:
                        logger.error(f"Config listener error: {e}")
                        
                return True
                
            except Exception as e:
                logger.error(f"Config update failed: {e}")
                return False
```

### Flet UI Patterns

#### Async Component Updates
```python
class DictationView:
    def __init__(self, page: ft.Page):
        self.page = page
        self.transcript_text = ft.Text("", selectable=True, size=16)
        self.status_icon = ft.Icon(ft.icons.CIRCLE, color=ft.colors.GREEN, size=12)
        self.confidence_bar = ft.ProgressBar(value=0, width=200)
        
    def build(self) -> ft.Control:
        """Build UI component hierarchy"""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    self.status_icon,
                    ft.Text("PersonalParakeet", weight=ft.FontWeight.BOLD),
                    self.confidence_bar
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(height=1),
                
                self.transcript_text,
                
                self._build_control_panel()
            ]),
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK),
            border_radius=12,
            padding=16,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.with_opacity(0.3, ft.colors.BLACK)
            )
        )
        
    async def update_transcript(self, text: str, confidence: float = 1.0):
        """Thread-safe transcript update"""
        self.transcript_text.value = text
        self.confidence_bar.value = confidence
        
        # Update status color based on activity
        if text.strip():
            self.status_icon.color = ft.colors.BLUE  # Active
        else:
            self.status_icon.color = ft.colors.GREEN  # Ready
            
        await self.page.update_async()
        
    async def show_error(self, error_message: str):
        """Display error with auto-dismiss"""
        self.status_icon.color = ft.colors.RED
        self.transcript_text.value = f"Error: {error_message}"
        await self.page.update_async()
        
        # Auto-clear after 3 seconds
        await asyncio.sleep(3)
        self.status_icon.color = ft.colors.GREEN
        self.transcript_text.value = ""
        await self.page.update_async()
```

#### Draggable Window Pattern
```python
class DraggableWindow:
    def __init__(self, page: ft.Page):
        self.page = page
        self.dragging = False
        self.drag_start = None
        
    def make_draggable(self, container: ft.Container) -> ft.Container:
        """Add drag functionality to container"""
        
        def on_pan_start(e):
            self.dragging = True
            self.drag_start = (e.global_x, e.global_y)
            
        def on_pan_update(e):
            if self.dragging and self.drag_start:
                dx = e.global_x - self.drag_start[0]
                dy = e.global_y - self.drag_start[1]
                
                # Update window position
                self.page.window_left = max(0, self.page.window_left + dx)
                self.page.window_top = max(0, self.page.window_top + dy)
                self.page.update()
                
                self.drag_start = (e.global_x, e.global_y)
                
        def on_pan_end(e):
            self.dragging = False
            self.drag_start = None
            
        # Add gesture detector
        return ft.GestureDetector(
            content=container,
            on_pan_start=on_pan_start,
            on_pan_update=on_pan_update,
            on_pan_end=on_pan_end,
            drag_interval=10
        )
```

---

## Platform-Specific Implementations

### Windows Text Injection

#### UI Automation (Preferred)
```python
class WindowsUIAutomation:
    """Windows UI Automation - most reliable"""
    
    def __init__(self):
        try:
            import uiautomation as auto
            self.automation = auto
            self.available = True
        except ImportError:
            self.available = False
            
    def inject_text(self, text: str) -> bool:
        if not self.available:
            return False
            
        try:
            focused = self.automation.GetFocusedControl()
            if focused:
                # Try different injection methods
                if hasattr(focused, 'SendKeys'):
                    focused.SendKeys(text)
                    return True
                elif hasattr(focused, 'SetValue'):
                    pattern = focused.GetValuePattern()
                    if pattern:
                        current = pattern.Value or ""
                        pattern.SetValue(current + text)
                        return True
        except Exception as e:
            logger.debug(f"UI Automation failed: {e}")
            
        return False
```

#### Win32 SendInput
```python
class Win32SendInput:
    """Direct Windows API injection"""
    
    def __init__(self):
        try:
            import win32api, win32con
            self.win32api = win32api
            self.win32con = win32con
            self.available = True
        except ImportError:
            self.available = False
            
    def inject_text(self, text: str) -> bool:
        if not self.available:
            return False
            
        try:
            for char in text:
                # Send key down and up events
                vk_code = self.win32api.VkKeyScanEx(char, 0)
                if vk_code != -1:
                    self.win32api.keybd_event(
                        vk_code & 0xFF, 0, 0, 0
                    )
                    self.win32api.keybd_event(
                        vk_code & 0xFF, 0, self.win32con.KEYEVENTF_KEYUP, 0
                    )
            return True
        except Exception as e:
            logger.debug(f"Win32 SendInput failed: {e}")
            return False
```

### Linux Text Injection

#### X11 Injection
```python
class X11Injection:
    """X11-based text injection for Linux"""
    
    def __init__(self):
        try:
            from Xlib import X, XK, display
            from Xlib.ext import record
            self.X = X
            self.XK = XK
            self.display = display.Display()
            self.available = True
        except ImportError:
            self.available = False
            
    def inject_text(self, text: str) -> bool:
        if not self.available:
            return False
            
        try:
            # Get focused window
            focus_window = self.display.get_input_focus().focus
            
            for char in text:
                # Convert character to keysym
                keysym = ord(char)
                keycode = self.display.keysym_to_keycode(keysym)
                
                if keycode:
                    # Send key press and release
                    focus_window.send_event(
                        X.KeyPress,
                        detail=keycode,
                        time=X.CurrentTime
                    )
                    focus_window.send_event(
                        X.KeyRelease,
                        detail=keycode,
                        time=X.CurrentTime
                    )
                    
            self.display.sync()
            return True
            
        except Exception as e:
            logger.debug(f"X11 injection failed: {e}")
            return False
```

#### Wayland/KDE Support
```python
class KDEWaylandManager:
    """KDE Wayland text injection via KDE-specific APIs"""
    
    def __init__(self):
        self.available = self._check_kde_availability()
        
    def _check_kde_availability(self) -> bool:
        """Check if running on KDE Wayland"""
        try:
            import subprocess
            result = subprocess.run(['qdbus', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
            
    def inject_text(self, text: str) -> bool:
        if not self.available:
            return False
            
        try:
            import subprocess
            
            # Use KDE's clipboard integration
            subprocess.run(['qdbus', 'org.kde.klipper', '/klipper', 
                          'setClipboardContents', text], check=True)
            
            # Simulate Ctrl+V
            subprocess.run(['qdbus', 'org.kde.KWin', '/VirtualKeyboard',
                          'org.kde.KWin.VirtualKeyboard.sendKey',
                          'ctrl+v'], check=True)
            
            return True
            
        except Exception as e:
            logger.debug(f"KDE Wayland injection failed: {e}")
            return False
```

---

## Performance Optimization

### GPU Memory Management
```python
class GPUMemoryManager:
    """Manage GPU memory for large models"""
    
    def __init__(self):
        self.allocated_memory = 0
        self.memory_threshold = 0.8  # 80% of GPU memory
        
    def check_memory_available(self, required_mb: int) -> bool:
        """Check if enough GPU memory is available"""
        if not torch.cuda.is_available():
            return False
            
        gpu_memory = torch.cuda.get_device_properties(0).total_memory
        gpu_memory_mb = gpu_memory / (1024 * 1024)
        current_allocated = torch.cuda.memory_allocated() / (1024 * 1024)
        
        available = gpu_memory_mb - current_allocated
        return available > required_mb
        
    def optimize_for_inference(self, model):
        """Optimize model for inference"""
        model.eval()
        
        # Enable optimizations
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.enabled = True
        
        # Use inference mode context
        model = torch.jit.optimize_for_inference(model)
        
        return model
        
    def clear_cache_if_needed(self):
        """Clear GPU cache if memory usage is high"""
        if torch.cuda.is_available():
            memory_usage = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
            if memory_usage > self.memory_threshold:
                torch.cuda.empty_cache()
                logger.info("GPU cache cleared")
```

### Audio Processing Optimization
```python
class AudioOptimizer:
    """Optimize audio processing for real-time performance"""
    
    def __init__(self, sample_rate=16000, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.audio_buffer = collections.deque(maxlen=10)
        
    def optimize_audio_chunk(self, audio_data: np.ndarray) -> np.ndarray:
        """Optimize audio data for STT processing"""
        
        # Normalize audio
        audio_data = audio_data.astype(np.float32)
        audio_data = audio_data / np.max(np.abs(audio_data))
        
        # Apply noise reduction (simple high-pass filter)
        from scipy import signal
        b, a = signal.butter(3, 100, 'high', fs=self.sample_rate)
        audio_data = signal.filtfilt(b, a, audio_data)
        
        # Ensure correct sample rate
        if len(audio_data) != self.chunk_size:
            audio_data = signal.resample(audio_data, self.chunk_size)
            
        return audio_data
        
    def batch_audio_chunks(self, min_batch_size=3) -> Optional[np.ndarray]:
        """Batch multiple chunks for more efficient processing"""
        if len(self.audio_buffer) >= min_batch_size:
            batched = np.concatenate(list(self.audio_buffer))
            self.audio_buffer.clear()
            return batched
        return None
```

---

## Error Handling Patterns

### Graceful Degradation
```python
class GracefulDegradationManager:
    """Handle component failures gracefully"""
    
    def __init__(self):
        self.component_status = {}
        self.fallback_strategies = {}
        
    def register_component(self, name: str, component, fallback=None):
        """Register component with optional fallback"""
        self.component_status[name] = "healthy"
        self.fallback_strategies[name] = fallback
        
    def handle_component_failure(self, component_name: str, error: Exception):
        """Handle component failure with fallback"""
        logger.error(f"Component {component_name} failed: {error}")
        self.component_status[component_name] = "failed"
        
        fallback = self.fallback_strategies.get(component_name)
        if fallback:
            logger.info(f"Activating fallback for {component_name}")
            return fallback
        else:
            logger.warning(f"No fallback available for {component_name}")
            return None
            
    def get_system_health(self) -> dict:
        """Get overall system health status"""
        total = len(self.component_status)
        healthy = sum(1 for status in self.component_status.values() 
                     if status == "healthy")
        
        return {
            "overall_health": healthy / total if total > 0 else 0,
            "components": self.component_status.copy(),
            "degraded": healthy < total
        }
```

---

**Last Updated**: July 26, 2025  
**Related Documentation**: [ARCHITECTURE.md](ARCHITECTURE.md), [DEVELOPMENT.md](DEVELOPMENT.md), [STATUS.md](STATUS.md)