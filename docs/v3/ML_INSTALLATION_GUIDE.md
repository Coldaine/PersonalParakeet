# PersonalParakeet v3 - ML Installation Guide

This guide covers the modern hybrid approach using Poetry for Python dependencies and Conda for ML/CUDA dependencies. This separation provides better compatibility and easier GPU management.

## 🚀 Quick Start

### Automated Installation (Recommended)
```bash
# From project root
./install.sh  # Linux/Mac
# OR
install.bat   # Windows
```

Choose:
- **Option 1**: Full installation with ML/CUDA support (for real STT)
- **Option 2**: Base installation with mock STT only (for development/testing)

## 📋 Prerequisites

1. **Poetry** - Python dependency management
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Conda** - ML/CUDA dependency management
   - Download Miniconda: https://docs.conda.io/en/latest/miniconda.html
   - Or Anaconda: https://www.anaconda.com/products/individual

## 🔧 Manual Installation

### Step 1: Install Python Dependencies
```bash
# From project root
poetry install
```

This installs all non-ML dependencies:
- Rust UI framework (compiled via maturin)
- Audio libraries (sounddevice, numpy, scipy)
- Utility libraries (keyboard, pyperclip, etc.)

### Step 2: Install ML Dependencies (Optional)

#### Create Conda Environment
```bash
conda env create -f environment.yml -n personalparakeet
```

This installs:
- PyTorch with CUDA 12.1 support
- CUDA toolkit and cuDNN
- NeMo toolkit for speech recognition
- Audio processing libraries optimized for CUDA

#### Update Existing Environment
```bash
conda env update -f environment.yml -n personalparakeet
```

## 🎯 Usage

### For Development (Mock STT)
```bash
# Just use Poetry
poetry shell
python main.py
```

### For Production (Real STT)
```bash
# Activate both environments
poetry shell
conda activate personalparakeet
python main.py

# Don't forget to update config.json:
# Set "use_mock_stt": false
```

## 🖥️ Platform-Specific Notes

### RTX 5090 / Latest GPUs
The environment.yml includes PyTorch 2.1.2 with CUDA 12.1. For RTX 5090:
```bash
# May need PyTorch nightly
conda activate personalparakeet
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
```

### CPU-Only Installation
To create a CPU-only environment:
```bash
# Edit environment.yml and remove:
# - pytorch-cuda=12.1
# - cudatoolkit=12.1
# - cudnn=8.9.2
# - onnxruntime-gpu (change to onnxruntime)

conda env create -f environment.yml -n personalparakeet-cpu
```

### WSL2 / Linux
Ensure NVIDIA drivers are properly installed:
```bash
nvidia-smi  # Should show your GPU
```

## ⚙️ Configuration

### config.json Settings
```json
{
  "audio": {
    "use_mock_stt": false,    // false for real STT, true for mock
    "stt_device": "cuda",     // "cuda" or "cpu"
    "stt_model_path": null,   // Path to local model (optional)
    "stt_audio_threshold": 0.01
  }
}
```

### Environment Variables
```bash
# Force CPU even if CUDA available
export PERSONALPARAKEET_STT_DEVICE=cpu

# Force mock STT
export PERSONALPARAKEET_USE_MOCK_STT=true

# Custom model path
export PERSONALPARAKEET_MODEL_PATH=/path/to/model
```

## 🔍 Verification

### Check Installation
```bash
# Verify ML stack
python ml_stack_check.py

# Expected output for full installation:
# ✓ Python 3.11+
# ✓ CUDA 12.1
# ✓ PyTorch 2.1.2
# ✓ NeMo available
# ✓ GPU: NVIDIA GeForce RTX ...
```

### Test STT
```bash
# Test with real microphone
python test_live_audio.py

# Test full pipeline
python test_full_pipeline.py
```

## 🐛 Troubleshooting

### "No module named 'torch'"
You're in Poetry environment but not Conda:
```bash
conda activate personalparakeet
```

### "CUDA out of memory"
Reduce batch size or use CPU:
```bash
export PERSONALPARAKEET_STT_DEVICE=cpu
```

### "RuntimeError: CUDA error"
Check CUDA compatibility:
```bash
python -c "import torch; print(torch.cuda.is_available())"
nvidia-smi  # Check driver version
```

### Conda Environment Issues
```bash
# List environments
conda env list

# Remove and recreate
conda env remove -n personalparakeet
conda env create -f environment.yml -n personalparakeet
```

## 📊 Performance Expectations

| Configuration | STT Latency | GPU Memory | Suitable For |
|--------------|-------------|------------|--------------|
| RTX 4090/5090 | 50-100ms | 4-6GB | Real-time dictation |
| RTX 3060-3090 | 100-200ms | 4-6GB | Real-time dictation |
| GTX 1660/2060 | 200-400ms | 4GB | Casual use |
| CPU (i7/i9) | 1-5s | N/A | Development only |
| Mock STT | <10ms | N/A | Testing/Development |

## 🔗 Additional Resources

- [PyTorch Installation Guide](https://pytorch.org/get-started/locally/)
- [Conda Cheat Sheet](https://docs.conda.io/projects/conda/en/latest/user-guide/cheatsheet.html)
- [NeMo Documentation](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/stable/)
- [Poetry Documentation](https://python-poetry.org/docs/)

## 💡 Tips

1. **Development Workflow**: Use mock STT during UI development, switch to real STT for testing
2. **CI/CD**: Use base installation (Poetry only) for CI pipelines
3. **Docker**: Consider using NVIDIA Container Toolkit for containerized deployments
4. **Model Caching**: First run downloads ~4GB model, subsequent runs use cache

---

For issues or questions, see the [main README](../README.md) or open an issue on GitHub.
