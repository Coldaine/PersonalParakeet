#!/bin/bash
# Fix ML Dependencies for PersonalParakeet
# This script resolves all dependency conflicts and ensures proper ML stack installation

set -e  # Exit on error

echo "🔧 PersonalParakeet ML Dependency Fix Script"
echo "==========================================="
echo ""

# Check if we're in a conda environment
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "❌ Error: Not in a conda environment!"
    echo "Please run: conda activate personalparakeet"
    exit 1
fi

if [ "$CONDA_DEFAULT_ENV" != "personalparakeet" ]; then
    echo "⚠️  Warning: Currently in '$CONDA_DEFAULT_ENV' environment"
    echo "Recommended: conda activate personalparakeet"
    echo ""
fi

echo "📦 Step 1: Clean up conflicting packages"
echo "----------------------------------------"
# Uninstall conflicting packages to start fresh
poetry run pip uninstall -y fsspec datasets nemo-toolkit pytorch-lightning torchmetrics numba numpy 2>/dev/null || true

echo ""
echo "📦 Step 2: Install core dependencies in correct order"
echo "----------------------------------------------------"

# Install numpy first with correct version for Numba
echo "Installing numpy<2.0 for Numba compatibility..."
poetry run pip install "numpy<2.0"

# Install fsspec with NeMo-compatible version
echo "Installing fsspec==2024.12.0 for NeMo compatibility..."
poetry run pip install fsspec==2024.12.0

# Install numba
echo "Installing numba..."
poetry run pip install "numba>=0.60.0"

echo ""
echo "📦 Step 3: Install PyTorch stack (should already be installed)"
echo "-------------------------------------------------------------"
# Check if PyTorch is installed
if poetry run python -c "import torch" 2>/dev/null; then
    echo "✅ PyTorch is already installed"
    poetry run python -c "import torch; print(f'   Version: {torch.__version__}')"
    poetry run python -c "import torch; print(f'   CUDA available: {torch.cuda.is_available()}')"
    if poetry run python -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
        poetry run python -c "import torch; print(f'   GPU: {torch.cuda.get_device_name(0)}')"
    fi
else
    echo "Installing PyTorch for RTX 5090..."
    poetry run pip install -r requirements-torch.txt
fi

echo ""
echo "📦 Step 4: Install NeMo toolkit with specific versions"
echo "-----------------------------------------------------"
# Install pytorch-lightning with compatible version
echo "Installing pytorch-lightning..."
poetry run pip install "pytorch-lightning>=2.0.0,<2.3.0"

# Install torchmetrics with compatible version
echo "Installing torchmetrics..."
poetry run pip install "torchmetrics>=0.11.0,<1.5.0"

# Install librosa (audio processing)
echo "Installing librosa..."
poetry run pip install "librosa>=0.10.0"

# Finally install NeMo
echo "Installing nemo-toolkit[asr]..."
poetry run pip install --no-deps nemo-toolkit[asr]==2.4.0

# Install any missing NeMo dependencies
echo "Installing remaining NeMo dependencies..."
poetry run pip install hydra-core omegaconf sentencepiece sacremoses inflect editdistance

echo ""
echo "📦 Step 5: Verify installation"
echo "-----------------------------"
echo "Checking critical package versions..."
poetry run python << 'EOF'
import sys
print("Python packages status:")
print("-" * 40)

packages = [
    ("numpy", "numpy"),
    ("torch", "torch"),
    ("fsspec", "fsspec"),
    ("numba", "numba"),
    ("nemo", "nemo"),
    ("pytorch_lightning", "pytorch_lightning"),
    ("torchmetrics", "torchmetrics"),
]

for display_name, import_name in packages:
    try:
        module = __import__(import_name)
        version = getattr(module, "__version__", "unknown")
        print(f"✅ {display_name}: {version}")
        
        # Special checks
        if import_name == "torch":
            import torch
            print(f"   CUDA available: {torch.cuda.is_available()}")
            if torch.cuda.is_available():
                print(f"   CUDA version: {torch.version.cuda}")
                print(f"   GPU: {torch.cuda.get_device_name(0)}")
        elif import_name == "numpy":
            import numpy as np
            print(f"   NumPy API version: {np.version.version}")
    except ImportError as e:
        print(f"❌ {display_name}: NOT INSTALLED - {e}")
    except Exception as e:
        print(f"⚠️  {display_name}: ERROR - {e}")

print("-" * 40)

# Test NeMo import
print("\nTesting NeMo import...")
try:
    import nemo
    import nemo.collections.asr as nemo_asr
    print("✅ NeMo ASR module imports successfully")
except Exception as e:
    print(f"❌ NeMo import error: {e}")

# Test basic torch operations
print("\nTesting PyTorch operations...")
try:
    import torch
    x = torch.randn(2, 3)
    if torch.cuda.is_available():
        x = x.cuda()
        print("✅ CUDA tensor operations work")
    else:
        print("✅ CPU tensor operations work")
except Exception as e:
    print(f"❌ PyTorch operation error: {e}")
EOF

echo ""
echo "✅ Dependency fix complete!"
echo ""
echo "📝 Next steps:"
echo "1. Run: poetry run personalparakeet"
echo "2. If you still see errors, check the output above for any ❌ marks"
echo "3. For a complete reinstall, run: ./clean_install_ml.sh"
echo ""
echo "💡 Tips:"
echo "- Always activate conda environment: conda activate personalparakeet"
echo "- For development without ML: set use_mock_stt: true in config"
echo "- To verify GPU: poetry run python -c \"import torch; print(torch.cuda.is_available())\""