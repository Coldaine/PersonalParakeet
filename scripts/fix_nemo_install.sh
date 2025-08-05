#!/bin/bash
# Fix NeMo installation for PersonalParakeet

echo "=== PersonalParakeet NeMo Installation Fix ==="
echo

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda not found. Please install Anaconda/Miniconda first."
    exit 1
fi

# Check if in personalparakeet environment
if [[ "$CONDA_DEFAULT_ENV" != "personalparakeet" ]]; then
    echo "Activating personalparakeet conda environment..."
    eval "$(conda shell.bash hook)"
    conda activate personalparakeet
    
    if [[ "$CONDA_DEFAULT_ENV" != "personalparakeet" ]]; then
        echo "ERROR: Failed to activate personalparakeet environment"
        echo "Please run: conda activate personalparakeet"
        exit 1
    fi
fi

echo "✓ Conda environment: $CONDA_DEFAULT_ENV"
echo

# Check PyTorch installation
echo "Checking PyTorch installation..."
python -c "import torch; print(f'✓ PyTorch {torch.__version__} installed')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "✗ PyTorch not found in conda environment"
    echo "Installing PyTorch with CUDA support..."
    conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y
fi

# Check CUDA availability
python -c "import torch; print(f'✓ CUDA available: {torch.cuda.is_available()}')" 2>/dev/null

echo
echo "Installing NeMo toolkit in conda environment..."
echo "This may take several minutes..."

# Install NeMo and its dependencies directly in conda
# Using pip within conda environment to avoid Poetry conflicts
pip install --upgrade pip setuptools wheel

# Install core dependencies first
pip install hydra-core omegaconf pytorch-lightning toml

# Install NeMo without ASR dependencies first to avoid conflicts
pip install nemo_toolkit[core]

# Then install ASR-specific dependencies
pip install nemo_toolkit[asr]

echo
echo "Verifying NeMo installation..."
python -c "import nemo; print(f'✓ NeMo {nemo.__version__} installed successfully')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ NeMo installation verified"
else
    echo "✗ NeMo installation failed"
    echo "Please check the error messages above"
    exit 1
fi

echo
echo "Updating Poetry to sync with conda packages..."
# Remove nemo-toolkit from pyproject.toml to avoid conflicts
python << 'EOF'
import toml
from pathlib import Path

pyproject_path = Path('pyproject.toml')
data = toml.load(pyproject_path)

# Remove nemo-toolkit from dependencies
if 'nemo-toolkit' in data['tool']['poetry']['dependencies']:
    del data['tool']['poetry']['dependencies']['nemo-toolkit']
    print("✓ Removed nemo-toolkit from poetry dependencies")
    
    # Save updated pyproject.toml
    with open(pyproject_path, 'w') as f:
        toml.dump(data, f)
    print("✓ Updated pyproject.toml")
else:
    print("ℹ nemo-toolkit not found in poetry dependencies")
EOF

echo
echo "Running poetry install to sync remaining dependencies..."
poetry install

echo
echo "=== Installation Complete ==="
echo
echo "To test the installation, run:"
echo "  python -c 'from personalparakeet.core.stt_factory import STTFactory; print(STTFactory.get_stt_info())'"
echo
echo "To run PersonalParakeet:"
echo "  poetry run personalparakeet"
echo "  # or"
echo "  python run_background.py start"