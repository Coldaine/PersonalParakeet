#!/bin/bash
# PersonalParakeet v3 - Hybrid Installation Script (Poetry + Conda)

echo "🦜 PersonalParakeet v3 Installation"
echo "=================================="
echo "Using best practice Poetry + Conda hybrid approach"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Poetry
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed!"
    echo "Install from: https://python-poetry.org/docs/#installation"
    echo "Quick install: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi
echo "✅ Poetry found: $(poetry --version)"

# Check Conda
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed!"
    echo "Install Miniconda from: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi
echo "✅ Conda found: $(conda --version)"
echo ""

# Step 1: Install Python dependencies with Poetry
echo "📦 Step 1: Installing Python dependencies with Poetry..."
poetry install
if [ $? -ne 0 ]; then
    echo "❌ Poetry installation failed!"
    exit 1
fi
echo "✅ Poetry dependencies installed"
echo ""

# Step 2: Create/Update Conda environment for ML dependencies
echo "📦 Step 2: Setting up Conda environment for ML/CUDA..."

# Check for existing environment
if conda env list | grep -q "personalparakeet"; then
    echo "Updating existing conda environment..."
    eval "$(conda shell.bash hook)"
    conda activate personalparakeet
    conda env update -f environment.yml --prune
else
    echo "Creating new conda environment..."
    conda env create -f environment.yml -n personalparakeet
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "To run PersonalParakeet:"
    echo "  1. source ./activate.sh  (or manually activate both environments)"
    echo "  2. python -m personalparakeet"
    echo ""
    echo "The hybrid setup provides:"
    echo "  • Poetry: Manages Python packages and dependencies"
    echo "  • Conda: Manages ML frameworks and CUDA"
    echo ""
else
    echo ""
    echo "❌ Conda environment setup failed!"
    echo "Please check the error messages above."
    exit 1
fi