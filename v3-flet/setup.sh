#!/bin/bash

# PersonalParakeet v3 Setup Script
# This script sets up a virtual environment and installs dependencies

echo "Setting up PersonalParakeet v3 environment..."

# Check if Python 3.11+ is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$PYTHON_VERSION < 3.11" | bc -l) -eq 1 ]]; then
    echo "Error: Python 3.11 or higher is required (current: $PYTHON_VERSION)"
    exit 1
fi

echo "Using Python $PYTHON_VERSION"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv v3-flet-env

# Activate virtual environment
echo "Activating virtual environment..."
source v3-flet-env/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-v3.txt

# Install PyTorch with CUDA support
echo "Installing PyTorch with CUDA support..."
pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

echo "Setup complete!"
echo "To activate the environment in the future, run:"
echo "source v3-flet-env/bin/activate"

echo "To run the application:"
echo "python main.py"