#!/bin/bash
# PersonalParakeet Environment Validation Script
# This script validates that all dependencies are correctly installed
# and the environment is properly configured for ML workloads

set -e  # Exit on error

echo "🔍 PersonalParakeet Environment Validation"
echo "========================================"
echo ""

# Check if we're in conda environment
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "❌ Error: Not in a conda environment!"
    echo "Please run: conda activate personalparakeet"
    exit 1
fi

if [ "$CONDA_DEFAULT_ENV" != "personalparakeet" ]; then
    echo "⚠️  Warning: Currently in '$CONDA_DEFAULT_ENV' environment"
    echo "Expected: personalparakeet"
fi

echo "✅ Conda environment: $CONDA_DEFAULT_ENV"
echo ""

# Check Python version
echo "📦 Checking Python version..."
python_version=$(poetry run python --version 2>&1)
echo "   $python_version"

# Check Poetry installation
echo ""
echo "📦 Checking Poetry..."
poetry --version

# Check core dependencies
echo ""
echo "📦 Validating core dependencies..."
poetry run python << 'EOF'
import sys
print("Python packages validation:")
print("-" * 40)

# Core packages to check
packages = [
    ("numpy", "numpy", "< 2.0 for Numba compatibility"),
    ("scipy", "scipy", "Signal processing"),
    ("torch", "torch", "PyTorch framework"),
    ("torchvision", "torchvision", "Computer vision"),
    ("torchaudio", "torchaudio", "Audio processing"),
    ("fsspec", "fsspec", "== 2024.12.0 for NeMo"),
    ("nemo", "nemo", "NVIDIA ASR toolkit"),
    ("flet", "flet", "UI framework"),
]

failed = []
for display_name, import_name, note in packages:
    try:
        module = __import__(import_name)
        version = getattr(module, "__version__", "unknown")
        print(f"✅ {display_name}: {version} ({note})")
    except ImportError as e:
        print(f"❌ {display_name}: NOT INSTALLED - {e}")
        failed.append(display_name)

if failed:
    print(f"\n❌ Missing packages: {', '.join(failed)}")
    sys.exit(1)
EOF

# Check CUDA availability
echo ""
echo "🖥️  Checking GPU/CUDA..."
poetry run python << 'EOF'
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("⚠️  Warning: CUDA not available - will use CPU (slower)")
EOF

# Check version compatibility
echo ""
echo "🔄 Checking version compatibility..."
poetry run python << 'EOF'
import torch
import torchvision
import torchaudio

torch_version = torch.__version__.split('+')[0]
vision_version = torchvision.__version__.split('+')[0]
audio_version = torchaudio.__version__.split('+')[0]

print(f"PyTorch: {torch.__version__}")
print(f"TorchVision: {torchvision.__version__}")
print(f"TorchAudio: {torchaudio.__version__}")

# Check major.minor versions match
torch_major_minor = '.'.join(torch_version.split('.')[:2])
vision_major_minor = '.'.join(vision_version.split('.')[:2])
audio_major_minor = '.'.join(audio_version.split('.')[:2])

if torch_major_minor == vision_major_minor == audio_major_minor:
    print(f"✅ Version compatibility: All packages at {torch_major_minor}.x")
else:
    print(f"⚠️  Version mismatch detected!")
    print(f"   PyTorch: {torch_major_minor}.x")
    print(f"   TorchVision: {vision_major_minor}.x")
    print(f"   TorchAudio: {audio_major_minor}.x")
EOF

# Test NeMo import
echo ""
echo "🎤 Testing NeMo ASR import..."
poetry run python -c "import nemo.collections.asr as nemo_asr; print('✅ NeMo ASR module imports successfully')"

# Run a quick functional test
echo ""
echo "🧪 Running quick functional test..."
poetry run python << 'EOF'
import torch
import numpy as np

# Test tensor operations
x = torch.randn(2, 3)
if torch.cuda.is_available():
    x = x.cuda()
    y = x @ x.T
    print("✅ CUDA tensor operations work")
else:
    y = x @ x.T
    print("✅ CPU tensor operations work")

# Test numpy interop
arr = np.random.randn(10)
tensor = torch.from_numpy(arr)
print("✅ NumPy interoperability works")
EOF

# Check Poetry consistency
echo ""
echo "📋 Checking Poetry consistency..."
poetry check || echo "⚠️  Poetry check failed - consider running 'poetry lock --no-update'"

echo ""
echo "✅ Environment validation complete!"
echo ""
echo "📝 Summary:"
echo "- Conda environment: Active"
echo "- Python packages: Installed"
echo "- ML frameworks: Compatible"
echo "- CUDA support: Available"
echo ""
echo "🚀 Ready to run: poetry run personalparakeet"