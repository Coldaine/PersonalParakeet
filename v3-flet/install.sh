#!/bin/bash
# PersonalParakeet v3 - Hybrid Installation Script
# Uses Poetry for Python deps and Conda for ML/CUDA deps

set -e  # Exit on error

echo "🦜 PersonalParakeet v3 - Hybrid Installation"
echo "==========================================="
echo ""

# Check for required tools
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install $1 first."
        echo "   Visit: $2"
        exit 1
    fi
}

echo "📋 Checking prerequisites..."
check_command poetry "https://python-poetry.org/docs/#installation"
check_command conda "https://docs.conda.io/en/latest/miniconda.html"

# Detect installation type
echo ""
echo "🤔 Choose installation type:"
echo "1) Full installation (with ML/CUDA support)"
echo "2) Base installation (mock STT only)"
echo ""
read -p "Enter choice (1 or 2): " choice

# Step 1: Install Python dependencies with Poetry
echo ""
echo "📦 Installing Python dependencies with Poetry..."
poetry install

# Step 2: Handle ML dependencies based on choice
if [ "$choice" = "1" ]; then
    echo ""
    echo "🧠 Setting up ML environment with Conda..."
    
    # Create/update conda environment
    echo "Creating conda environment 'personalparakeet'..."
    conda env create -f environment.yml -n personalparakeet 2>/dev/null || \
    conda env update -f environment.yml -n personalparakeet
    
    echo ""
    echo "✅ Full installation complete!"
    echo ""
    echo "🚀 To use PersonalParakeet with ML support:"
    echo "   1. Activate Poetry shell: poetry shell"
    echo "   2. Activate Conda env: conda activate personalparakeet"
    echo "   3. Run: python main.py"
    echo ""
    echo "📝 Don't forget to update config.json:"
    echo '   Set "use_mock_stt": false for real STT'
    
else
    echo ""
    echo "✅ Base installation complete!"
    echo ""
    echo "🚀 To use PersonalParakeet with mock STT:"
    echo "   1. Activate Poetry shell: poetry shell"
    echo "   2. Run: python main.py"
    echo ""
    echo "📝 config.json is already set to use mock STT"
fi

echo ""
echo "📚 For more information, see docs/ML_INSTALLATION_GUIDE.md"
echo "🦜 Happy dictating!"