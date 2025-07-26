# PersonalParakeet v3 - ML Installation Guide

This guide covers installing the ML dependencies (PyTorch, NeMo) for real STT functionality.

## Quick Start

### Option 1: CPU-Only Installation (No GPU)
```bash
cd v3-flet/
poetry install --with ml
```

### Option 2: GPU Installation (Recommended)
```bash
cd v3-flet/
# First, install base dependencies
poetry install

# Then install ML dependencies with CUDA support
poetry run pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
poetry install --with ml
```

## Detailed Installation Instructions

### 1. Check Your System

First, verify your system setup:
```bash
python ml_stack_check.py
```

This will tell you:
- If you have a compatible GPU
- Current CUDA version
- What's already installed
- Specific recommendations for your system

### 2. Installation Paths

#### A. Development without GPU (CPU-Only)

Best for:
- Testing UI and non-ML features
- Development on laptops without NVIDIA GPU
- Initial setup and testing

```bash
# Using Poetry (recommended)
cd v3-flet/
poetry install --with ml

# OR using pip directly
pip install -r requirements-v3.txt
pip install nemo-toolkit[asr] torch torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**Pros:**
- Works on any system
- Smaller download size
- No CUDA requirements

**Cons:**
- Slower STT processing (5-10x slower)
- Not suitable for real-time dictation
- Will automatically fall back to mock STT if too slow

#### B. Production with GPU (CUDA)

Best for:
- Real-time dictation
- Production deployment
- Systems with NVIDIA GPU

**Standard CUDA 11.8 Installation:**
```bash
# Using Poetry
cd v3-flet/
poetry install
poetry run pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
poetry install --with ml

# OR using pip directly
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install nemo-toolkit[asr]
```

**CUDA 12.1 Installation (newer GPUs):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install nemo-toolkit[asr]
```

#### C. RTX 5090 Special Instructions

The RTX 5090 requires CUDA 12.8+ which may not be in stable PyTorch yet:

```bash
# Install PyTorch nightly with CUDA 12.8 support
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121

# Then install NeMo
pip install nemo-toolkit[asr]

# If you encounter issues, try the cuda_fix script from v2:
python ../v2_legacy_archive/personalparakeet/cuda_fix.py
```

### 3. Post-Installation Verification

After installation, verify everything works:

```bash
# Check ML stack
python ml_stack_check.py

# Test STT integration
python test_stt_integration.py

# Run the main app
python main.py
```

### 4. Configuration Options

You can control STT behavior via configuration:

```json
{
  "audio": {
    "use_mock_stt": false,    // Force mock STT even if NeMo available
    "stt_device": "cuda",     // "cuda" or "cpu"
    "stt_model_path": null,   // Path to local model file
    "stt_audio_threshold": 0.01
  }
}
```

Or via environment variables:
```bash
# Force CPU even if CUDA available
export PERSONALPARAKEET_STT_DEVICE=cpu

# Force mock STT
export PERSONALPARAKEET_USE_MOCK_STT=true
```

### 5. Troubleshooting

#### Issue: "ImportError: No module named nemo"
**Solution:** Install ML dependencies:
```bash
poetry install --with ml
# OR
pip install nemo-toolkit[asr]
```

#### Issue: "CUDA out of memory"
**Solutions:**
1. Use float16 precision (already implemented)
2. Reduce batch size in configuration
3. Close other GPU applications
4. Use CPU mode: `config.audio.stt_device = "cpu"`

#### Issue: "PyTorch not compiled with CUDA"
**Solution:** Reinstall PyTorch with correct CUDA version:
```bash
# First, uninstall existing PyTorch
pip uninstall torch torchvision torchaudio

# Then install with correct CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Issue: Mock STT being used despite NeMo installed
**Check:**
1. Run `python ml_stack_check.py` to verify installation
2. Check logs for import errors
3. Ensure `use_mock_stt` is not set to `true` in config

### 6. Performance Expectations

| Configuration | Latency | Accuracy | Hardware Requirements |
|--------------|---------|----------|----------------------|
| Mock STT | <50ms | N/A (simulated) | None |
| CPU Real STT | 500-2000ms | High | 8GB+ RAM |
| GPU Real STT | 50-200ms | High | NVIDIA GPU, 4GB+ VRAM |

### 7. Fallback Behavior

The STT Factory automatically falls back to mock if:
1. NeMo is not installed
2. Import errors occur
3. `use_mock_stt` is set to `true`
4. Insufficient GPU memory

This ensures the app always runs, even without ML dependencies.

## Next Steps

1. Run `ml_stack_check.py` to verify your setup
2. Test with `python main.py`
3. Configure settings in `config.json` as needed
4. For production, consider using PyInstaller with custom hooks for NeMo