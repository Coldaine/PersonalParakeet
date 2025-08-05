#!/bin/bash
# Clean Install ML Dependencies for PersonalParakeet
# This script performs a complete clean installation of ML dependencies

set -e  # Exit on error

echo "🧹 PersonalParakeet Clean ML Installation Script"
echo "=============================================="
echo ""
echo "⚠️  WARNING: This will remove and reinstall all ML packages!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read -r

# Check if we're in a conda environment
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "❌ Error: Not in a conda environment!"
    echo "Please run: conda activate personalparakeet"
    exit 1
fi

echo "📦 Step 1: Remove all ML-related packages"
echo "----------------------------------------"
# List of packages to remove
ML_PACKAGES=(
    "torch" "torchvision" "torchaudio" "pytorch-triton"
    "nemo-toolkit" "pytorch-lightning" "torchmetrics"
    "fsspec" "numba" "librosa" "datasets"
    "numpy" "scipy"
)

for package in "${ML_PACKAGES[@]}"; do
    echo "Removing $package..."
    poetry run pip uninstall -y "$package" 2>/dev/null || true
done

# Clean pip cache
echo "Cleaning pip cache..."
poetry run pip cache purge

echo ""
echo "📦 Step 2: Install base scientific stack"
echo "---------------------------------------"
# Install numpy with correct version first
echo "Installing numpy<2.0..."
poetry run pip install "numpy>=1.26.0,<2.0"

# Install scipy
echo "Installing scipy..."
poetry run pip install "scipy>=1.11.0"

echo ""
echo "📦 Step 3: Install PyTorch for RTX 5090"
echo "--------------------------------------"
echo "Installing from PyTorch nightly..."
poetry run pip install -r requirements-torch.txt

# Verify PyTorch installation
echo "Verifying PyTorch installation..."
poetry run python -c "import torch; print(f'PyTorch {torch.__version__} installed')"
poetry run python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"

echo ""
echo "📦 Step 4: Install ML dependencies in order"
echo "------------------------------------------"
# Install in specific order to avoid conflicts

# 1. fsspec (pinned for NeMo)
echo "Installing fsspec==2024.12.0..."
poetry run pip install fsspec==2024.12.0

# 2. numba
echo "Installing numba..."
poetry run pip install "numba>=0.60.0"

# 3. librosa
echo "Installing librosa..."
poetry run pip install "librosa>=0.10.0"

# 4. pytorch-lightning (before NeMo)
echo "Installing pytorch-lightning..."
poetry run pip install "pytorch-lightning>=2.0.0,<2.3.0"

# 5. torchmetrics
echo "Installing torchmetrics..."
poetry run pip install "torchmetrics>=0.11.0,<1.5.0"

# 6. NeMo dependencies
echo "Installing NeMo dependencies..."
poetry run pip install hydra-core omegaconf sentencepiece sacremoses inflect editdistance

# 7. Finally, NeMo itself (no deps to avoid conflicts)
echo "Installing nemo-toolkit..."
poetry run pip install --no-deps nemo-toolkit[asr]==2.4.0

echo ""
echo "📦 Step 5: Final verification"
echo "----------------------------"
poetry run python << 'EOF'
import sys
print("🔍 Verifying ML stack installation...")
print("=" * 50)

# Version checks
checks = {
    "Python": (sys.version.split()[0], ">=3.11"),
    "NumPy": (None, "<2.0"),
    "PyTorch": (None, ">=2.9.0"),
    "CUDA": (None, "12.8"),
    "NeMo": (None, "2.4.0"),
    "fsspec": (None, "2024.12.0"),
}

results = []

# Python version
results.append(("Python", sys.version.split()[0], True))

# NumPy
try:
    import numpy as np
    ver = np.__version__
    results.append(("NumPy", ver, ver.startswith("1.")))
except:
    results.append(("NumPy", "NOT INSTALLED", False))

# PyTorch
try:
    import torch
    results.append(("PyTorch", torch.__version__, True))
    results.append(("CUDA Available", str(torch.cuda.is_available()), torch.cuda.is_available()))
    if torch.cuda.is_available():
        results.append(("CUDA Version", torch.version.cuda, True))
        results.append(("GPU", torch.cuda.get_device_name(0), True))
except:
    results.append(("PyTorch", "NOT INSTALLED", False))

# fsspec
try:
    import fsspec
    results.append(("fsspec", fsspec.__version__, fsspec.__version__ == "2024.12.0"))
except:
    results.append(("fsspec", "NOT INSTALLED", False))

# NeMo
try:
    import nemo
    import nemo.collections.asr as nemo_asr
    results.append(("NeMo", nemo.__version__, True))
except:
    results.append(("NeMo", "NOT INSTALLED", False))

# numba
try:
    import numba
    results.append(("numba", numba.__version__, True))
except:
    results.append(("numba", "NOT INSTALLED", False))

# Print results
print("\nInstallation Status:")
print("-" * 50)
for name, version, status in results:
    icon = "✅" if status else "❌"
    print(f"{icon} {name:<20} {version}")

# Test import chain
print("\n🧪 Testing import chain...")
all_good = True
try:
    import torch
    import nemo
    import nemo.collections.asr as nemo_asr
    print("✅ All core imports successful!")
except Exception as e:
    print(f"❌ Import error: {e}")
    all_good = False

# Test CUDA operations
if all_good:
    print("\n🧪 Testing CUDA operations...")
    try:
        import torch
        if torch.cuda.is_available():
            x = torch.randn(100, 100).cuda()
            y = x @ x.T
            print("✅ CUDA operations successful!")
        else:
            print("⚠️  CUDA not available, CPU mode only")
    except Exception as e:
        print(f"❌ CUDA operation error: {e}")

print("\n" + "=" * 50)
if all([status for _, _, status in results]):
    print("✅ All checks passed! ML stack is ready.")
else:
    print("⚠️  Some components are missing. Check the errors above.")
EOF

echo ""
echo "🎉 Clean installation complete!"
echo ""
echo "📝 Next steps:"
echo "1. Run: poetry run personalparakeet"
echo "2. Ensure config has: \"use_mock_stt\": false"
echo "3. Test with: poetry run pytest tests/integration/test_full_pipeline.py"