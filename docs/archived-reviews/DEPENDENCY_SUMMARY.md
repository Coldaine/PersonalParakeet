# PersonalParakeet v3 - Comprehensive Dependency Analysis

## Executive Summary

PersonalParakeet v3 is a Python-based real-time speech-to-text dictation system with advanced AI corrections and a transparent floating UI. The project uses a **hybrid dependency management approach** combining Poetry for Python packages and Conda for ML/CUDA binaries to address the complex requirements of GPU-accelerated machine learning.

**Total Dependencies**: ~50+ packages across development, production, and ML stacks  
**Key Constraint**: RTX 5090 support requires PyTorch nightly builds with CUDA 12.8  
**Architecture**: Single-process Flet application (no WebSocket/multi-process complexity)

---

## 1. Dependency Management Strategy

### 1.1 Hybrid Approach Rationale

The project employs a **three-tier dependency management system**:

1. **Poetry** (`pyproject.toml`) - Core Python dependencies and project structure
2. **Pip Requirements** (`requirements-torch.txt`, `requirements-ml.txt`) - ML packages with complex version constraints  
3. **Conda** (`environment.yml`) - System-level binaries (CUDA toolkit, MKL)

### 1.2 Why Not Pure Poetry?

- **Version Conflicts**: NeMo, PyTorch, and their dependencies have strict, often conflicting version requirements
- **CUDA Complexity**: PyTorch's CUDA-specific versioning scheme conflicts with Poetry's resolver
- **RTX 5090 Support**: Requires nightly builds from specific PyTorch indices that Poetry struggles with
- **ML Ecosystem**: Many ML packages use complex dependency graphs that exceed Poetry's resolver capabilities

---

## 2. Core Production Dependencies

### 2.1 ML/Audio Processing Stack

| Category | Package | Version | Purpose | Notes |
|----------|---------|---------|---------|-------|
| **Deep Learning** | torch | 2.7.0 (CUDA 12.8) | Core PyTorch framework | RTX 5090 Blackwell support |
| | torchvision | 0.22.0 | Computer vision utilities | Paired with PyTorch version |
| | torchaudio | 2.7.0 | Audio processing | Native audio ML operations |
| | pytorch-lightning | ^2.0.0,<2.3.0 | Training framework | NeMo dependency constraint |
| | torchmetrics | ^0.11.0,<1.5.0 | ML metrics | NeMo compatibility |
| **Speech Recognition** | nemo-toolkit[asr] | ^2.4.0 | NVIDIA speech models | Core STT engine (Parakeet) |
| | numba | >=0.60.0 | JIT compilation | Required by NeMo components |
| | librosa | >=0.10.0 | Audio analysis | NeMo ASR dependency |
| **Scientific Computing** | numpy | ^1.26.0,<2.0 | Numerical arrays | Pinned <2.0 for Numba compatibility |
| | scipy | ^1.11.0 | Scientific algorithms | Audio processing utilities |
| **Configuration** | hydra-core | ^1.3.2 | Configuration management | NeMo's config system |
| | omegaconf | ^2.3.0 | Config objects | Structured configs |

### 2.2 Audio I/O & Hardware

| Package | Version | Purpose | Platform Notes |
|---------|---------|---------|----------------|
| sounddevice | ^0.4.6 | Real-time audio capture | Cross-platform PortAudio wrapper |
| soundfile | ^0.12.0 | Audio file I/O | libsndfile bindings |
| pyaudio | ^0.2.11 | Alternative audio interface | Windows compatibility |

### 2.3 UI Framework

| Package | Version | Purpose | Architecture Decision |
|---------|---------|---------|----------------------|
| flet | ^0.28.3 | Python-native UI | Replaced Tauri/React for single-process |

### 2.4 System Integration

| Package | Version | Purpose | Platform Support |
|---------|---------|---------|-------------------|
| keyboard | ^0.13.5 | Global hotkeys | Cross-platform input capture |
| pynput | ^1.8.1 | Alternative input handling | Backup for keyboard |
| pyperclip | ^1.9.0 | Clipboard operations | Text injection mechanism |
| python-dotenv | ^1.0.0 | Environment variables | Configuration loading |

### 2.5 Data & Utilities

| Package | Version | Purpose | Usage Context |
|---------|---------|---------|---------------|
| dataclasses-json | ^0.6.0 | Config serialization | Type-safe configuration |
| networkx | ^3.5 | Graph algorithms | Thought linking system |
| packaging | ^25.0 | Version utilities | Dependency validation |
| cython | ^3.1.2 | C extensions | Performance optimizations |

---

## 3. Development Dependencies

### 3.1 Testing Framework

| Package | Version | Purpose | Features |
|---------|---------|---------|----------|
| pytest | ^7.0.0 | Test runner | Core testing framework |
| pytest-asyncio | ^0.21.0 | Async test support | Flet UI testing |
| pytest-cov | ^4.0.0 | Coverage reporting | Test coverage analysis |

### 3.2 Code Quality & Formatting

| Package | Version | Purpose | Configuration |
|---------|---------|---------|---------------|
| black | ^24.3.0 | Code formatting | Line length: 100 |
| isort | ^5.12.0 | Import sorting | Black profile |
| ruff | ^0.8.0 | Fast linting | Modern flake8 replacement |
| mypy | ^1.0.0 | Type checking | Strict type validation |
| flake8 | ^6.0.0 | Legacy linting | Backup linter |

### 3.3 Development Tools

| Package | Version | Purpose | Usage |
|---------|---------|---------|-------|
| openai-whisper | ^20250625 | STT comparison | Benchmarking against OpenAI |
| gtts | ^2.5.4 | Text-to-speech | Test audio generation |

---

## 4. Special Dependencies & Constraints

### 4.1 RTX 5090 Support Requirements

**Challenge**: RTX 5090 uses Blackwell architecture (sm_120 compute capability) which requires bleeding-edge PyTorch builds.

**Solution**:
```toml
[[tool.poetry.source]]
name = "pytorch-cu128"
url = "https://download.pytorch.org/whl/cu128"
priority = "explicit"

torch = { version = "2.7.0", source = "pytorch-cu128" }
```

**Fallback** (requirements-torch.txt):
```
--index-url https://download.pytorch.org/whl/nightly/cu128
torch>=2.9.0.dev20250804
```

### 4.2 NeMo Compatibility Matrix

**Critical Constraints**:
- `numpy < 2.0` - Numba doesn't support NumPy 2.x
- `fsspec == 2024.12.0` - Exact version required
- `pytorch-lightning < 2.3.0` - Breaking changes in newer versions

### 4.3 Installation Order Dependencies

**Strict Installation Sequence** (see `fix_ml_dependencies.sh`):
1. Core scientific stack (numpy, scipy)
2. PyTorch with CUDA
3. Fixed versions (fsspec, numba, librosa)
4. PyTorch ecosystem (lightning, metrics)
5. NeMo (with --no-deps flag)
6. Missing NeMo dependencies

---

## 5. Architecture Impact of Dependencies

### 5.1 Single-Process Architecture

**Key Decision**: Migrated from Tauri (Rust + Node.js + Python) to pure Python Flet
- **Eliminated**: WebSocket dependencies, IPC complexity
- **Added**: Flet (~50MB) for rich UI
- **Result**: Single executable, simplified deployment

### 5.2 Threading Model

**Dependencies Supporting Threading**:
- `queue.Queue` - Thread-safe audio pipeline
- `asyncio` - UI updates via `run_coroutine_threadsafe()`
- `sounddevice` - Callback-based audio capture

### 5.3 Configuration System

**Dependencies**:
- `dataclasses-json` - Type-safe config serialization
- `omegaconf` - Structured configurations (NeMo integration)
- `hydra-core` - Advanced config management

---

## 6. Dependency Installation & Management

### 6.1 Quick Installation

```bash
# Environment setup
conda activate personalparakeet
./fix_ml_dependencies.sh        # Quick fix
./clean_install_ml.sh          # Complete reinstall
```

### 6.2 Development Workflow

```bash
# Base setup (UI development)
poetry install

# ML setup (STT development)  
conda activate personalparakeet
poetry install
poetry run pip install -r requirements-torch.txt
```

### 6.3 Verification Commands

```bash
# Check all imports
poetry run python -c "import torch, nemo, numpy; print('Success')"

# Check CUDA
poetry run python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# Check versions
poetry run pip list | grep -E "(torch|nemo|numpy)"
```

---

## 7. Dependency Conflicts & Solutions

### 7.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "No module named 'nemo'" | Complex NeMo dependencies | `pip install --no-deps nemo-toolkit[asr]==2.4.0` |
| "numpy.dtype size changed" | NumPy C API conflicts | `pip install --force-reinstall numba` |
| fsspec version conflicts | Dataset packages want newer | `pip install --force-reinstall fsspec==2024.12.0` |
| CUDA not detected | Wrong PyTorch build | Reinstall from requirements-torch.txt |

### 7.2 Dependency Health Monitoring

**Files to watch**:
- `pyproject.toml` - Core dependencies
- `requirements-torch.txt` - GPU dependencies  
- `requirements-ml.txt` - ML-specific packages
- `fix_ml_dependencies.sh` - Installation automation

---

## 8. Future Dependency Strategy

### 8.1 Maintenance Considerations

1. **PyTorch Updates**: Always verify RTX 5090 compatibility
2. **NeMo Updates**: May require adjusting entire ML stack
3. **NumPy 2.x Migration**: Blocked by Numba support timeline
4. **Poetry vs Requirements**: Continue hybrid approach until Poetry improves ML support

### 8.2 Potential Improvements

1. **Docker**: NVIDIA Container Toolkit for reproducible environments
2. **Conda-forge**: More packages available via conda for better compatibility
3. **Lock Files**: Pin exact versions for production deployments
4. **CI Matrix**: Test multiple Python/PyTorch combinations

---

## 9. Environment Files Reference

| File | Purpose | Contents |
|------|---------|----------|
| `pyproject.toml` | Poetry dependencies | Non-ML packages, dev tools, project config |
| `requirements-torch.txt` | PyTorch CUDA | GPU-accelerated PyTorch for RTX 5090 |
| `requirements-ml.txt` | ML packages | NeMo and constrained versions |
| `environment.yml` | Conda environment | System binaries (CUDA toolkit, MKL) |
| `fix_ml_dependencies.sh` | Installation script | Automated dependency resolution |
| `clean_install_ml.sh` | Clean install | Complete environment rebuild |

---

## 10. Dependency Size & Performance Impact

### 10.1 Package Sizes (Approximate)

- **PyTorch Stack**: ~3.5GB (CUDA libraries included)
- **NeMo Toolkit**: ~500MB (models downloaded separately) 
- **Flet Framework**: ~50MB (includes Flutter engine)
- **Audio Libraries**: ~100MB (PortAudio, libsndfile)
- **Dev Tools**: ~200MB (pytest, black, mypy, etc.)

**Total Environment**: ~4.5GB for full ML setup

### 10.2 Runtime Performance

- **Cold Start**: 3-5 seconds (model loading)
- **Memory Usage**: 4-6GB GPU VRAM, 2-3GB system RAM
- **STT Latency**: 50-200ms (GPU-dependent)

---

This dependency analysis reflects the current state as of August 2025 and should be updated as the project evolves and dependencies change.