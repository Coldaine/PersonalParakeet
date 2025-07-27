# PersonalParakeet - Quick Start Guide

Get PersonalParakeet v3 running in under 5 minutes.

## Prerequisites

- Python 3.11+
- NVIDIA GPU (optional - for real-time STT)
- 8GB RAM minimum

## Installation

### 1. Clone and Setup

```bash
git clone <repository>
cd PersonalParakeet/v3-flet

# Option A: With Poetry (recommended)
poetry install --with ml

# Option B: With pip
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements-v3.txt
```

### 2. Verify Installation

```bash
# Check system compatibility
python ml_stack_check.py

# Expected output:
# ✓ Python 3.11+
# ✓ CUDA available (optional)
# ✓ Audio device detected
```

### 3. Run PersonalParakeet

```bash
# With Poetry
poetry run python main.py

# With venv activated
python main.py
```

## First Time Setup

### Audio Device
PersonalParakeet will auto-detect your microphone. To select a specific device:

```bash
# List available devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Set in config.json
{"audio": {"audio_device_index": 2}}
```

### GPU vs CPU Mode

**GPU Mode (default)** - Real-time performance
```json
{"audio": {"stt_device": "cuda", "use_mock_stt": false}}
```

**CPU Mode** - No GPU required, slower
```json
{"audio": {"stt_device": "cpu", "use_mock_stt": false}}
```

**Mock Mode** - Testing without ML dependencies
```json
{"audio": {"use_mock_stt": true}}
```

## Usage

1. **Start Dictation** - Launch the app
2. **Speak** - Your words appear in real-time
3. **Pause** - 1.5 second pause auto-commits text
4. **Drag** - Move the window anywhere

### Keyboard Shortcuts
- **ESC** - Clear current text
- **Enter** - Commit text immediately
- **Click & Drag** - Reposition window

## Troubleshooting

### No Audio Input
```bash
# Test microphone
python test_live_audio.py
```

### GPU Not Detected
```bash
# Force CPU mode
export PERSONALPARAKEET_STT_DEVICE=cpu
python main.py
```

### Import Errors
```bash
# Ensure you're in the virtual environment
which python  # Should show .venv path

# Reinstall dependencies
pip install -r requirements-v3.txt
```

## Next Steps

- Configure advanced settings in `config.json`
- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- See [DEVELOPMENT.md](DEVELOPMENT.md) for contributing

---

**Need Help?** Check [STATUS.md](STATUS.md) for known issues or file a GitHub issue.