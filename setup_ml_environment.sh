#!/bin/bash
# PersonalParakeet ML Environment Setup Script
# This script sets up the complete ML environment with proper dependency management

set -e  # Exit on error

echo "=== PersonalParakeet ML Environment Setup ==="
echo "This script will set up the complete ML environment for RTX 5090 support"
echo ""

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "Error: Conda is not installed. Please install Miniconda or Anaconda first."
    echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check if we're in the project directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Please run this script from the PersonalParakeet project root directory"
    exit 1
fi

echo "Step 1: Creating/updating Conda environment..."
if conda env list | grep -q "personalparakeet"; then
    echo "Updating existing personalparakeet environment..."
    conda env update -f environment.yml -n personalparakeet
else
    echo "Creating new personalparakeet environment..."
    conda env create -f environment.yml -n personalparakeet
fi

echo ""
echo "Step 2: Activating Conda environment..."
source $(conda info --base)/etc/profile.d/conda.sh
conda activate personalparakeet

echo ""
echo "Step 3: Installing Poetry dependencies (excluding ML packages)..."
poetry install --no-root

echo ""
echo "Step 4: Installing PyTorch nightly for RTX 5090..."
pip install -r requirements-torch.txt --upgrade

echo ""
echo "Step 5: Verifying PyTorch installation..."
python -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'GPU compute capability: {torch.cuda.get_device_capability(0)}')
"

echo ""
echo "Step 6: Installing ML dependencies (NeMo toolkit)..."
# Install fsspec first to avoid conflicts
pip install fsspec==2024.12.0

# Install NeMo and its dependencies
pip install nemo-toolkit[asr]==2.4.0

# Install remaining ML dependencies
pip install -r requirements-ml.txt

echo ""
echo "Step 7: Installing project in editable mode..."
poetry install

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To use the environment:"
echo "1. Activate conda: conda activate personalparakeet"
echo "2. Run the application: poetry run python -m personalparakeet"
echo ""
echo "To verify the installation:"
echo "Run: python validate_environment.py"
echo ""