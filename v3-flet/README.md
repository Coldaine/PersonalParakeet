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
- CUDA-compatible GPU (recommended for real-time STT)
- NeMo toolkit and PyTorch (for real STT - see ML Installation Guide)

## Setup

### Quick Installation (Recommended)

```bash
# Run the installation script
./install.sh  # Linux/Mac
install.bat   # Windows
```

Choose:
- **Option 1**: Full installation with ML/CUDA support (for real STT)
- **Option 2**: Base installation with mock STT only (for development)

### Manual Installation

#### Step 1: Install Prerequisites

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install Miniconda (if not already installed)
# Download from: https://docs.conda.io/en/latest/miniconda.html
```

#### Step 2: Install Dependencies

```bash
# Install Python dependencies
poetry install

# For ML support, also create conda environment
conda env create -f environment.yml -n personalparakeet
```

#### Step 3: Activate Environments

```bash
# For development (mock STT)
poetry shell

# For production (real STT)
poetry shell
conda activate personalparakeet
```

**⚠️ Important**: ML dependencies are now managed by Conda for better CUDA compatibility.

For RTX 5090 and other modern GPUs:

```bash
# With Poetry
poetry add torch torchvision torchaudio --source https://download.pytorch.org/whl/nightly/cu128

# With pip in venv
pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

## Running the Application

```bash
# With Poetry
poetry run python main.py

# With activated venv
python main.py
```

### First Run

1. **Check ML Stack**: Verify your ML dependencies are properly installed:
   ```bash
   python ml_stack_check.py
   ```

2. **Configure STT Mode**: 
   - For real STT (default): Ensure NeMo is installed
   - For mock STT (testing): Set `"use_mock_stt": true` in config.json

3. **Launch**: The app will show a clear error if ML dependencies are missing

See [docs/ML_INSTALLATION_GUIDE.md](docs/ML_INSTALLATION_GUIDE.md) for detailed ML setup instructions.

## Project Structure

```
v3-flet/
├── main.py              # Entry point
├── config.py            # Configuration system
├── audio_engine.py      # Audio processing pipeline
├── core/                # Core processing modules
│   ├── stt_processor.py # Real STT with NeMo/Parakeet
│   ├── stt_processor_mock.py # Mock STT for testing
│   ├── stt_factory.py   # STT factory with fallback
│   ├── cuda_compatibility.py # CUDA/GPU detection
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
# With Poetry
poetry run pytest tests/
poetry run pytest tests/test_command_processor.py

# With activated venv
python -m pytest tests/
python -m pytest tests/test_command_processor.py
```

### Code Formatting

```bash
# With Poetry
poetry run black .
poetry run isort .
poetry run mypy .

# With activated venv (after installing dev dependencies)
black .
isort .
mypy .
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