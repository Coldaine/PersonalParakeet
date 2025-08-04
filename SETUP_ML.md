# PersonalParakeet ML Dependencies Setup Guide

## 🚨 Current Dependency Solution

This document explains the hybrid dependency management approach for PersonalParakeet, which uses:
- **Poetry**: For pure Python dependencies and project management
- **Pip with requirements files**: For ML dependencies that have complex version constraints
- **Conda**: For system-level binaries (CUDA toolkit, MKL, etc.)

## Why This Approach?

1. **Poetry limitations**: Poetry's dependency resolver struggles with PyTorch's CUDA-specific versioning and the complex dependency graph of ML libraries
2. **Version conflicts**: NeMo, PyTorch, and their dependencies have strict version requirements that often conflict
3. **RTX 5090 support**: Requires PyTorch nightly builds from specific indices

## Quick Fix for Current Issues

Run the fix script:
```bash
conda activate personalparakeet
./fix_ml_dependencies.sh
```

For a complete clean install:
```bash
conda activate personalparakeet
./clean_install_ml.sh
```

## Manual Installation Steps

### 1. Base Environment Setup
```bash
# Create/update conda environment (system binaries only)
conda env create -f environment.yml -n personalparakeet
conda activate personalparakeet

# Install Poetry dependencies (non-ML packages)
poetry install
```

### 2. ML Dependencies Installation Order

**Critical**: Install in this exact order to avoid conflicts

```bash
# 1. Core scientific stack
poetry run pip install "numpy>=1.26.0,<2.0"  # Must be <2.0 for Numba
poetry run pip install "scipy>=1.11.0"

# 2. PyTorch for RTX 5090
poetry run pip install -r requirements-torch.txt

# 3. Fixed versions for NeMo compatibility
poetry run pip install fsspec==2024.12.0
poetry run pip install "numba>=0.60.0"
poetry run pip install "librosa>=0.10.0"

# 4. PyTorch ecosystem
poetry run pip install "pytorch-lightning>=2.0.0,<2.3.0"
poetry run pip install "torchmetrics>=0.11.0,<1.5.0"

# 5. NeMo toolkit (no-deps to avoid conflicts)
poetry run pip install --no-deps nemo-toolkit[asr]==2.4.0

# 6. Missing NeMo dependencies
poetry run pip install hydra-core omegaconf sentencepiece sacremoses inflect editdistance
```

### 3. Verification
```bash
# Check all packages
poetry run python -c "import torch, nemo, numpy; print('All imports successful')"

# Check versions
poetry run pip list | grep -E "(torch|nemo|numpy|fsspec)"

# Check CUDA
poetry run python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

## Dependency Constraints Explained

### numpy < 2.0
- **Why**: Numba (required by NeMo) doesn't support NumPy 2.x yet
- **Impact**: Limits us to NumPy 1.x ecosystem

### fsspec == 2024.12.0
- **Why**: NeMo 2.4.0 specifically requires this version
- **Conflicts**: datasets and other packages want newer versions
- **Solution**: Pin to exact version, install early in sequence

### PyTorch Nightly
- **Why**: RTX 5090 requires sm_120 compute capability (Blackwell architecture)
- **Source**: `--index-url https://download.pytorch.org/whl/nightly/cu128`

### pytorch-lightning < 2.3.0
- **Why**: NeMo 2.4.0 isn't compatible with newer versions
- **Impact**: Can't use latest Lightning features

## Common Issues and Solutions

### "No module named 'nemo'"
```bash
# NeMo failed to install, reinstall:
poetry run pip install --no-deps nemo-toolkit[asr]==2.4.0
poetry run pip install hydra-core omegaconf
```

### "numpy.dtype size changed" warning
```bash
# Rebuild packages that use NumPy C API:
poetry run pip install --force-reinstall --no-deps numba
```

### fsspec version conflicts
```bash
# Force the correct version:
poetry run pip install --force-reinstall fsspec==2024.12.0
```

### CUDA not detected
```bash
# Verify CUDA toolkit in conda:
conda list cuda-toolkit
# Should show cuda-toolkit 12.8

# Reinstall PyTorch:
poetry run pip install --force-reinstall -r requirements-torch.txt
```

## Development Workflow

### For UI/Non-ML Development
```bash
# Use mock STT to avoid ML dependencies
# In config.json: "use_mock_stt": true
poetry run personalparakeet
```

### For ML/STT Development
```bash
# Ensure conda environment is active
conda activate personalparakeet
# Run with real STT
# In config.json: "use_mock_stt": false
poetry run personalparakeet
```

## CI/CD Considerations

For CI pipelines without GPU:
```bash
# Install base dependencies only
poetry install
# Set environment variable
export PERSONALPARAKEET_USE_MOCK_STT=true
# Run tests
poetry run pytest tests/unit/
```

## Maintenance Notes

1. **Updating PyTorch**: Always check RTX 5090 compatibility
2. **Updating NeMo**: May require adjusting all ML package versions
3. **Adding ML packages**: Test full installation sequence after changes

## File Reference

- `pyproject.toml`: Poetry dependencies (non-ML)
- `requirements-torch.txt`: PyTorch with CUDA 12.8
- `requirements-ml.txt`: ML packages with pinned versions
- `environment.yml`: Conda environment (system binaries)
- `fix_ml_dependencies.sh`: Quick fix for dependency issues
- `clean_install_ml.sh`: Complete reinstallation

## Future Improvements

Consider:
1. Docker with NVIDIA Container Toolkit for reproducible environments
2. Separate conda environments for different CUDA versions
3. Migration to newer NeMo when NumPy 2.x support is added