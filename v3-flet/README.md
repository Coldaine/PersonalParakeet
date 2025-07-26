# PersonalParakeet v3 - Flet Implementation

PersonalParakeet v3 is a complete rewrite of the dictation system using Flet for the UI instead of the previous Tauri/React architecture. This version runs as a single Python process with integrated UI.

## Features

- Real-time speech-to-text using NVIDIA Parakeet-TDT
- AI-powered text corrections with the Clarity Engine
- Voice Activity Detection (VAD) for automatic pause detection
- Command mode with voice commands ("Hey Parakeet")
- Flet-based UI that floats on top of other applications
- Cross-platform text injection (Windows/Linux)

## Prerequisites

- Python 3.11 or higher
- CUDA-compatible GPU (recommended for best performance)

## Setup

### 1. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv v3-flet-env

# Activate virtual environment
# On Windows:
v3-flet-env\Scripts\activate
# On macOS/Linux:
source v3-flet-env/bin/activate
```

### 2. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements-v3.txt

# Or install with Flet support using pyproject.toml
pip install -e .[flet]
```

### 3. Install PyTorch with CUDA Support

For RTX 5090 and other modern GPUs, install the latest PyTorch:

```bash
pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

## Running the Application

```bash
# Run the main application
python main.py
```

## Project Structure

```
v3-flet/
├── main.py              # Entry point
├── config.py            # Configuration system
├── audio_engine.py      # Audio processing pipeline
├── core/                # Core processing modules
│   ├── stt_processor.py # Speech-to-text processing
│   ├── clarity_engine.py # Text correction engine
│   ├── vad_engine.py    # Voice activity detection
│   ├── command_processor.py # Voice command processing
│   └── injection_manager.py # Text injection
├── ui/                  # Flet UI components
│   ├── dictation_view.py # Main UI
│   ├── components.py    # Reusable UI components
│   └── theme.py         # UI theming
└── tests/               # Unit tests
```

## Configuration

The application uses a dataclass-based configuration system. Default settings are in `config.py`, but you can override them by creating a `config.json` file in the project directory.

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_command_processor.py
```

### Code Formatting

```bash
# Format code with Black
black .

# Sort imports with isort
isort .
```

## Troubleshooting

### CUDA Issues

If you encounter CUDA compatibility issues with RTX 5090:

1. Ensure you have the latest PyTorch nightly build installed
2. Check that your CUDA drivers are up to date
3. Run the CUDA fix script: `python ../scripts/fix_rtx5090_pytorch.py`

### Audio Device Issues

If the application can't access your microphone:

1. Check that your microphone is properly connected
2. Verify that your system's audio settings allow the application to access the microphone
3. Try specifying a specific audio device in the configuration