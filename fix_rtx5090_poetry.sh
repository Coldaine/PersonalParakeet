#!/bin/bash
# RTX 5090 PyTorch Compatibility Fix for Poetry Environment

echo "========================================"
echo "RTX 5090 PyTorch Compatibility Fix"
echo "For Poetry-managed environment"
echo "========================================"
echo

# Get Poetry virtual environment path
VENV_PATH=$(poetry env info --path)
if [ -z "$VENV_PATH" ]; then
    echo "Error: Poetry environment not found. Please run 'poetry install' first."
    exit 1
fi

echo "Poetry environment: $VENV_PATH"
echo

# Step 1: Remove existing PyTorch
echo "Step 1: Removing existing PyTorch installation..."
poetry run pip uninstall -y torch torchvision torchaudio

# Also remove from pyproject.toml to prevent conflicts
echo "Removing PyTorch from pyproject.toml dependencies..."
python3 << 'EOF'
import toml
from pathlib import Path

pyproject_path = Path('pyproject.toml')
data = toml.load(pyproject_path)

# Remove PyTorch-related packages
deps = data['tool']['poetry']['dependencies']
removed = []
for pkg in ['torch', 'torchvision', 'torchaudio']:
    if pkg in deps:
        del deps[pkg]
        removed.append(pkg)

if removed:
    with open(pyproject_path, 'w') as f:
        toml.dump(data, f)
    print(f"✓ Removed from pyproject.toml: {', '.join(removed)}")
else:
    print("ℹ PyTorch packages not found in pyproject.toml")
EOF

echo
echo "Step 2: Installing PyTorch nightly build for RTX 5090 (Blackwell sm_120)..."
echo "This is the CRITICAL fix - RTX 5090 requires CUDA 12.8+ support!"
echo

# Install PyTorch nightly with CUDA 12.8 support
poetry run pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

echo
echo "Step 3: Verifying installation..."
echo

# Test the installation
poetry run python -c "
import torch
print(f'PyTorch Version: {torch.__version__}')
print(f'CUDA Available: {torch.cuda.is_available()}')
print(f'CUDA Version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}')

if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    capability = torch.cuda.get_device_capability(0)
    print(f'Compute Capability: {capability}')
    
    # Test CUDA kernel
    try:
        x = torch.randn(10, 10).cuda()
        y = x * 2
        print('✓ CUDA kernel test: PASSED')
    except Exception as e:
        print(f'✗ CUDA kernel test: FAILED - {e}')
else:
    print('✗ CUDA not available')
"

echo
echo "========================================"
echo "If you see Compute Capability: (12, 0) or (9, 0) above,"
echo "and CUDA kernel test PASSED, the fix worked!"
echo
echo "You can now run: poetry run python launch.py"
echo "========================================"