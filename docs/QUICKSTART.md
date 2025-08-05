
# PersonalParakeet v3 - Quick Start Guide (Last updated: August 4, 2025)

Get PersonalParakeet v3 running in under 5 minutes.

## Prerequisites

- Python 3.11+ (recommended: 3.11.x for ML compatibility)
- NVIDIA GPU (optional, for real-time STT)
- 8GB RAM minimum
- Conda (for environment management)
- Poetry (for dependency management)

## Installation

### 1. Clone and Setup

```bash
# Clone repository

cd PersonalParakeet

# Create conda environment with ML dependencies
conda env create -f environment.yml
conda activate personalparakeet

# Install application dependencies with Poetry
poetry install
```

### 2. Verify Installation

```bash
# Check system compatibility
poetry run python -m personalparakeet.scripts.ml_stack_check

# Expected output:
# ✓ Python 3.11+
# ✓ CUDA available (optional)
# ✓ Audio device detected
```

### 3. Run PersonalParakeet

```bash
# With Poetry
poetry run personalparakeet

# Or with python -m
python -m personalparakeet
```

## First Time Setup

### Audio Device Selection
PersonalParakeet will auto-detect your microphone. To select a specific device:

```bash
# List available devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Set in config.json (or use the configuration UI if available)
{
  "audio": {"device_index": 2}
}
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

- Configure advanced settings in `config.json` or via the configuration UI (if available)
- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- See [DEVELOPMENT.md](DEVELOPMENT.md) for contributing

---

**Need Help?** Check [STATUS.md](STATUS.md) for known issues or file a GitHub issue.
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