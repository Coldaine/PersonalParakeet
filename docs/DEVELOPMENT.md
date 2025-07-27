# PersonalParakeet v3 - Development Guide

Complete setup, development, and contribution guide for PersonalParakeet v3.

---

## Prerequisites

- **Python 3.11+**
- **NVIDIA GPU** (recommended for real-time STT) or CPU-only mode
- **CUDA 11.8+** for GPU acceleration
- **Poetry** (recommended) or pip with virtual environments

---

## Environment Setup

### Option 1: Poetry (Recommended)

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup
git clone <repository>
cd PersonalParakeet/v3-flet

# Install core dependencies (includes mock STT)
poetry install

# For real STT with NeMo/PyTorch
poetry install --with ml

# Activate environment
poetry shell
```

### Option 2: Virtual Environment

```bash
# Clone repository
git clone <repository>
cd PersonalParakeet/v3-flet

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Linux/WSL:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements-v3.txt
```

### Option 3: GPU/CUDA Setup

For RTX 5090 and other modern GPUs:

```bash
# With Poetry - PyTorch with CUDA 12.1
poetry run pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# With pip in venv - PyTorch with CUDA 12.1  
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Then install NeMo
poetry install --with ml
# OR: pip install nemo-toolkit[asr]
```

### ML Stack Verification

```bash
# Check your system compatibility
python ml_stack_check.py

# Expected output:
# ✓ GPU: NVIDIA GeForce RTX 5090 (32GB VRAM)
# ✓ CUDA: 12.1 compatible
# ✓ PyTorch: 2.6.0+cu121
# ✓ NeMo: Available
# ✓ Audio: HyperX QuadCast detected
```

**Important**: Never use `--break-system-packages`. Always use Poetry or virtual environments.

---

## Project Structure

```
v3-flet/
├── main.py                      # Entry point - Flet app
├── config.py                    # Dataclass configuration system
├── audio_engine.py              # Producer-consumer audio pipeline
├── ml_stack_check.py            # System compatibility checker
├── pyproject.toml               # Poetry configuration
├── requirements-v3.txt          # Pip requirements
├── ui/                          # Flet UI components
│   ├── dictation_view.py        # Main floating UI window
│   ├── components.py            # Reusable UI elements
│   └── theme.py                 # Material Design theme
├── core/                        # Core processing modules
│   ├── stt_processor.py         # Real STT with NeMo/Parakeet  
│   ├── stt_processor_mock.py    # Mock STT for testing
│   ├── stt_factory.py           # STT factory with fallback
│   ├── cuda_compatibility.py    # CUDA/GPU detection
│   ├── clarity_engine.py        # Text correction engine
│   ├── vad_engine.py            # Voice activity detection
│   ├── injection_manager.py     # Text injection strategies
│   ├── command_processor.py     # Voice command processing
│   └── thought_linker.py        # Multi-sentence composition
├── tests/                       # Test suite
│   ├── test_ui_basic.py         # Basic UI component tests
│   ├── test_audio_headless.py   # Audio pipeline tests
│   ├── test_stt_integration.py  # STT integration tests
│   └── test_live_audio.py       # Live microphone tests
└── docs/                        # v3-specific documentation
    └── ML_INSTALLATION_GUIDE.md # Detailed ML setup
```

---

## Development Commands

### Running the Application

```bash
# With Poetry
poetry run python main.py

# With activated venv
python main.py

# Check ML dependencies first
python ml_stack_check.py
```

### Testing

```bash
# Run all tests
poetry run pytest tests/

# Run specific test categories
python test_ui_basic.py          # UI components (no hardware)
python test_audio_headless.py    # Audio pipeline (no microphone)
python test_stt_integration.py   # STT integration (requires ML)
python test_live_audio.py        # Live microphone test (requires hardware)

# Skip hardware-dependent tests
pytest -m "not hardware"
```

### Code Quality

```bash
# Format code
poetry run black . --line-length 100
poetry run isort . --profile black

# Type checking
poetry run mypy . --ignore-missing-imports

# Linting
poetry run flake8 .
```

### Packaging (When Ready)

```bash
# Create executable
poetry run pyinstaller --onefile --windowed main.py

# Test package on clean system
# (Copy dist/main.exe to system without Python)
```

---

## Configuration

### Configuration Files

The application uses a dataclass-based configuration system:

**Default Configuration** (`config.py`):
```python
@dataclass
class AppConfig:
    # Audio settings
    audio_device_index: Optional[int] = None
    sample_rate: int = 16000
    
    # STT settings  
    use_mock_stt: bool = False
    stt_device: str = "cuda"           # "cuda" or "cpu"
    stt_model_path: Optional[str] = None
    
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

**User Configuration** (`config.json`):
```json
{
  "audio": {
    "use_mock_stt": false,
    "stt_device": "cuda",
    "sample_rate": 16000,
    "audio_device_index": null
  },
  "vad": {
    "threshold": 0.01,
    "pause_duration_ms": 1500  
  },
  "clarity": {
    "enabled": true
  },
  "ui": {
    "window_opacity": 0.9,
    "always_on_top": true,
    "theme_mode": "dark"
  }
}
```

### Environment Variables

```bash
# Force CPU even if CUDA available
export PERSONALPARAKEET_STT_DEVICE=cpu

# Force mock STT for testing
export PERSONALPARAKEET_USE_MOCK_STT=true

# Specify custom model path
export PERSONALPARAKEET_MODEL_PATH=/path/to/model
```

---

## STT Configuration Options

### Mock STT (Testing/Development)
```bash
# Set in config.json
{"audio": {"use_mock_stt": true}}

# Or environment variable
export PERSONALPARAKEET_USE_MOCK_STT=true
```
- **Pros**: No ML dependencies, instant startup, predictable output
- **Cons**: Not real transcription, limited testing value

### CPU STT (Compatibility)
```bash
# Set in config.json  
{"audio": {"stt_device": "cpu"}}

# Or environment variable
export PERSONALPARAKEET_STT_DEVICE=cpu
```
- **Pros**: Works on any system, no GPU required
- **Cons**: 5-10x slower, not suitable for real-time use

### GPU STT (Production)
```bash
# Default configuration - requires CUDA setup
{"audio": {"stt_device": "cuda", "use_mock_stt": false}}
```
- **Pros**: Real-time performance, high accuracy
- **Cons**: Requires NVIDIA GPU, larger setup

---

## Development Patterns

### Threading Architecture

```python
# Audio Producer (callback thread)
def audio_callback(indata, frames, time, status):
    """Runs in sounddevice thread - keep minimal"""
    if status:
        print(f"Audio callback status: {status}")
    audio_queue.put(indata.copy())

# STT Consumer (dedicated thread)  
def stt_worker(page):
    """Processes audio chunks - CPU/GPU intensive"""
    while self.running:
        try:
            chunk = audio_queue.get(timeout=1.0)
            text = stt_model.transcribe(chunk)
            
            # Thread-safe UI update
            asyncio.run_coroutine_threadsafe(
                update_ui(text), page.loop
            )
        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"STT error: {e}")

# Main Thread (Flet UI)
async def update_ui(text):
    """All UI updates must happen in main thread"""
    transcript_display.value = text
    await page.update_async()
```

### Flet UI Patterns

```python
class DictationView:
    def __init__(self, page):
        self.page = page
        self.transcript = ft.Text("", selectable=True)
        self.status_icon = ft.Icon(ft.icons.CIRCLE, color=ft.colors.GREEN)
        
    def build(self):
        """Build UI component tree"""
        return ft.Container(
            content=ft.Column([
                self.status_icon,
                self.transcript,
                self._build_controls()
            ]),
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.BLACK),
            border_radius=10,
            padding=20
        )
        
    async def update_transcript(self, text):
        """Thread-safe transcript update"""
        self.transcript.value = text
        await self.page.update_async()
```

### Configuration Loading

```python
from config import AppConfig, load_config

# Load with user overrides
config = load_config()

# Access typed settings
if config.audio.use_mock_stt:
    stt = MockSTTProcessor()
else:
    stt = RealSTTProcessor(device=config.audio.stt_device)
```

---

## Migration Guidelines

When porting v2 code to v3:

### 1. Remove WebSocket Code
```python
# OLD (v2)
await websocket.send(json.dumps({
    "type": "transcription", 
    "data": {"text": text}
}))

# NEW (v3)
await dictation_view.update_transcript(text)
```

### 2. Replace Process Calls
```python
# OLD (v2)  
backend_proc = subprocess.Popen([...])

# NEW (v3)
stt_thread = threading.Thread(target=self.stt_worker, daemon=True)
stt_thread.start()
```

### 3. Use Flet Reactive State
```python
# OLD (v2 - React/TypeScript)
const [transcript, setTranscript] = useState('')

# NEW (v3 - Flet/Python)
self.transcript_text = ft.Text("")
async def update_transcript(self, text):
    self.transcript_text.value = text
    await self.page.update_async()
```

### 4. Preserve Business Logic
- **Keep**: Algorithm implementations, correction rules, detection logic
- **Change**: Integration layer, communication methods, state management
- **Test**: Ensure same outputs for same inputs

---

## Troubleshooting

### CUDA Issues

**Problem**: `RuntimeError: No CUDA GPUs available`
```bash
# Check CUDA installation
nvidia-smi

# Verify PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with correct CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Problem**: RTX 5090 compatibility warnings
```bash
# Use PyTorch nightly for latest GPU support
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
```

### Audio Issues

**Problem**: `OSError: No Default Input Device Available`
```bash
# List available devices
python -c "import sounddevice as sd; print(sd.query_devices())"

# Test microphone access
python test_live_audio.py
```

**Problem**: Permission denied (Linux)
```bash
# Add user to audio group
sudo usermod -a -G audio $USER
# Logout and login again
```

### Import Errors

**Problem**: `ImportError: No module named 'nemo'`
```bash
# Install ML dependencies
poetry install --with ml
# OR: pip install nemo-toolkit[asr]
```

**Problem**: `ImportError: No module named 'flet'`
```bash
# Install core dependencies
poetry install
# OR: pip install flet>=0.28.0
```

### Performance Issues

**Problem**: High memory usage
- Check GPU memory: `nvidia-smi`
- Use CPU mode: `export PERSONALPARAKEET_STT_DEVICE=cpu`
- Reduce batch size in configuration

**Problem**: Audio dropouts
- Check audio queue overflow in logs
- Reduce audio device sample rate
- Close other audio applications

---

## Contributing

### Development Workflow

1. **Fork and clone** the repository
2. **Create feature branch**: `git checkout -b feature/my-feature`
3. **Install dependencies**: `poetry install --with ml`
4. **Run tests**: `poetry run pytest`
5. **Make changes** following patterns above
6. **Test thoroughly** including hardware tests
7. **Format code**: `poetry run black . && poetry run isort .`
8. **Commit and push**: Standard git workflow
9. **Create pull request** with clear description

### Code Standards

- **Black formatting** with 100-character line length
- **Type hints** for all function signatures
- **Docstrings** for public methods
- **Error handling** with proper logging
- **Thread safety** for concurrent code

### Testing Requirements

- **Unit tests** for all new components
- **Integration tests** for end-to-end functionality
- **Hardware tests** must not break on systems without hardware
- **Cross-platform testing** on Windows and Linux

---

## References

- [Architecture Decisions](ARCHITECTURE.md)
- [Current Status](STATUS.md)  
- [Technical Reference](TECHNICAL_REFERENCE.md)
- [ML Installation Guide](../v3-flet/docs/ML_INSTALLATION_GUIDE.md)

---

## Component Reference

### Core Components

#### Clarity Engine
Real-time text correction system (<150ms latency):
- **Homophones**: `too/to`, `your/you're`, `there/their/they're`
- **Technical Terms**: `clod code` → `claude code`, `get hub` → `github`
- **Programming**: `pie torch` → `pytorch`, `dock her` → `docker`

#### STT Processor
NVIDIA Parakeet-TDT 1.1B with intelligent fallback:
```python
# Factory pattern for STT
stt = STTFactory.create_processor(config)
# Returns: RealSTTProcessor (GPU/CPU) or MockSTTProcessor
```

#### VAD Engine  
Voice activity detection with pause detection:
- Default threshold: 0.01 RMS
- Default pause: 1.5 seconds
- Auto-commit on natural pauses

#### Text Injection
Multi-strategy system with automatic fallback:
1. UI Automation (Windows - most reliable)
2. Win32 SendInput
3. Keyboard injection
4. Clipboard fallback

### Platform-Specific Code

#### Windows
```python
# UI Automation (preferred)
import uiautomation as auto
focused = auto.GetFocusedControl()
focused.SendKeys(text)

# Win32 API fallback
import win32api
win32api.keybd_event(vk_code, 0, 0, 0)
```

#### Linux
```python
# X11 injection
from Xlib import X, display
display.Display().get_input_focus().focus.send_event(...)

# Wayland via KDE APIs
subprocess.run(['qdbus', 'org.kde.klipper', ...])
```

### Performance Optimization

#### GPU Memory Management
```python
# RTX 5090 optimizations
model.to(dtype=torch.float16)  # Use FP16
torch.backends.cudnn.benchmark = True

# Clear cache on OOM
try:
    result = model.transcribe(chunk)
except torch.cuda.OutOfMemoryError:
    torch.cuda.empty_cache()
```

#### Threading Best Practices
```python
# Audio producer (minimal processing)
def audio_callback(indata, frames, time, status):
    audio_queue.put(indata.copy())

# STT consumer (heavy processing)
def stt_worker():
    chunk = audio_queue.get()
    text = model.transcribe(chunk)
    asyncio.run_coroutine_threadsafe(update_ui(text), page.loop)
```

---

**Last Updated**: July 26, 2025