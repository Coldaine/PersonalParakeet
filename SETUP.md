# PersonalParakeet Setup Guide

This guide provides comprehensive instructions for setting up the PersonalParakeet development environment with full RTX 5090 support using a clean, modern dependency management approach.

## Prerequisites

### Hardware Requirements
- **NVIDIA RTX 5090** (Blackwell architecture, sm_120)
- **NVIDIA Driver R570** or higher
- Physical microphone (no mock hardware)
- 16GB+ RAM recommended

### Software Requirements
- Linux (Ubuntu 22.04+ recommended) or Windows 11
- Conda or Miniconda installed
- Git

## Dependency Management Architecture

PersonalParakeet uses a **streamlined two-tier dependency management system**:

1. **Conda**: System-level binaries and CUDA toolkit only
2. **Poetry**: Everything else, including PyTorch with explicit source management

This approach leverages Poetry's `explicit` source priority feature to cleanly handle PyTorch's custom package index while maintaining a single source of truth for all Python dependencies in `pyproject.toml`.

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/PersonalParakeet.git
cd PersonalParakeet

# 2. Create and activate conda environment
conda env create -f environment.yml
conda activate personalparakeet

# 3. Verify CUDA installation
nvidia-smi  # Should show your RTX 5090
nvcc --version  # Should show CUDA 12.8

# 4. Install all Python dependencies with Poetry
poetry install

# 5. Verify PyTorch CUDA support
poetry run python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0)}')"

# 6. Run validation script
poetry run python validate_environment.py
```

## Detailed Setup Instructions

### Step 1: Conda Environment

Create the minimal conda environment:

```bash
conda env create -f environment.yml
conda activate personalparakeet
```

This installs only:
- Python 3.11
- CUDA toolkit 12.8 (required for RTX 5090)
- System libraries (MKL, portaudio)
- Build tools for C extensions
- Poetry itself

### Step 2: Poetry Installation

All Python dependencies, including PyTorch, are managed by Poetry:

```bash
poetry install
```

Poetry will:
1. Read `pyproject.toml` and resolve all dependencies
2. Download PyTorch from the CUDA 12.8 index (using the `explicit` source)
3. Install all other packages from PyPI
4. Create a `poetry.lock` file for reproducible installs

### Step 3: Switching PyTorch Versions

#### Using Stable PyTorch (Default)
The default configuration uses stable PyTorch 2.7.0 with CUDA 12.8 support.

#### Switching to Nightly Builds
If you need bleeding-edge RTX 5090 optimizations:

1. Edit `pyproject.toml`
2. Comment out the stable PyTorch lines
3. Uncomment the nightly build lines
4. Run `poetry update torch torchvision torchaudio`

```toml
# Comment these:
# torch = { version = "2.7.0", source = "pytorch-cu128" }
# torchvision = { version = "0.22.0", source = "pytorch-cu128" }
# torchaudio = { version = "2.7.0", source = "pytorch-cu128" }

# Uncomment these:
torch = { version = "^2.9.0.dev20250804", source = "pytorch-nightly", allow-prereleases = true }
torchvision = { version = "*", source = "pytorch-nightly", allow-prereleases = true }
torchaudio = { version = "*", source = "pytorch-nightly", allow-prereleases = true }
```

## Development Workflow

### Running the Application
```bash
# Using Poetry script
poetry run personalparakeet

# Or activate the Poetry shell
poetry shell
personalparakeet
```

### Running Tests
```bash
# All tests
poetry run pytest

# Specific test
poetry run pytest tests/integration/test_full_pipeline.py

# With coverage
poetry run pytest --cov=personalparakeet
```

### Code Quality
```bash
# Format code
poetry run black . --line-length 100
poetry run isort . --profile black

# Lint
poetry run ruff check .

# Type checking
poetry run mypy .
```

### Adding Dependencies
```bash
# Add a regular dependency
poetry add some-package

# Add a dev dependency
poetry add --group dev some-dev-package

# Add a package from the PyTorch index
# Edit pyproject.toml and add: package = { version = "x.y.z", source = "pytorch-cu128" }
```

## Troubleshooting

### "CUDA capability sm_120 is not compatible"

This means PyTorch doesn't support your RTX 5090:
1. Ensure you're using Poetry's installed PyTorch: `poetry run python -m torch.utils.collect_env`
2. Try switching to nightly builds (see above)

### "No kernel image available for execution"

Your PyTorch build doesn't include sm_120 support:
1. Update to latest: `poetry update torch torchvision torchaudio`
2. Check PyTorch version: `poetry show torch`

### Poetry dependency resolution is slow

This is normal when using custom sources. First-time resolution can take a few minutes. Subsequent installs use the lock file and are much faster.

### NeMo installation fails

NeMo has complex dependencies. Ensure:
1. You're using `poetry install` (not pip)
2. PyTorch is properly installed first
3. You have enough disk space (NeMo downloads large models)

## Environment Variables

Create a `.env` file for configuration:
```bash
# GPU settings
CUDA_VISIBLE_DEVICES=0  # Use first GPU
TF_FORCE_GPU_ALLOW_GROWTH=true

# NeMo settings
NEMO_CACHE_DIR=~/.cache/nemo
HYDRA_FULL_ERROR=1  # Show full error traces

# Application settings
PARAKEET_LOG_LEVEL=INFO
PARAKEET_MODEL=stt_en_citrinet_256
```

## Benefits of This Approach

1. **Single Source of Truth**: All dependencies in `pyproject.toml`
2. **Reproducible Builds**: `poetry.lock` ensures exact versions
3. **Clean Separation**: Conda handles only system binaries
4. **Easy PyTorch Management**: Switch between stable/nightly with a simple edit
5. **No Tool Conflicts**: Poetry manages the entire Python stack
6. **Fast Resolution**: Explicit sources prevent unnecessary index queries

## Validation

The setup includes a validation script that checks:
- Python version
- CUDA availability and version
- PyTorch installation and GPU support
- NeMo toolkit availability
- All required packages

Run it with:
```bash
poetry run python validate_environment.py
```

## Notes for CI/CD

For automated environments:
```bash
# Install from lock file (faster, deterministic)
poetry install --no-interaction --no-ansi

# Export requirements if needed for Docker
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Additional Resources

- [Poetry Documentation - Dependency Sources](https://python-poetry.org/docs/repositories/#package-sources)
- [PyTorch Get Started](https://pytorch.org/get-started/locally/)
- [NVIDIA RTX 5090 Developer Guide](https://developer.nvidia.com/rtx-5090)
- [NeMo Toolkit Documentation](https://docs.nvidia.com/nemo-framework/user-guide/latest/)