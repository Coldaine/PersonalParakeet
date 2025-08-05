#!/bin/bash
# PersonalParakeet - Activate both Poetry and Conda environments

echo "🦜 Activating PersonalParakeet environments..."

# Initialize conda
eval "$(conda shell.bash hook)"

# Check if conda environment exists
if ! conda env list | grep -q "personalparakeet"; then
    echo "❌ Conda environment 'personalparakeet' not found!"
    echo "Run ./install.sh first"
    exit 1
fi

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed!"
    echo "Install from: https://python-poetry.org/docs/#installation"
    exit 1
fi

# Activate conda environment
echo "📦 Activating Conda environment..."
conda activate personalparakeet

# Check Poetry dependencies
echo "📦 Checking Poetry dependencies..."
poetry install --no-root 2>/dev/null || poetry install

echo "✅ Both environments active!"
echo ""
echo "You can now run:"
echo "  python -m personalparakeet"
echo ""

# Start a new shell with both environments active
$SHELL