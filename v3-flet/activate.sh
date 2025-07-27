#!/bin/bash
# PersonalParakeet v3 - Environment Activation Helper

echo "🦜 PersonalParakeet v3 - Activating Environments"
echo "=============================================="
echo ""

# Function to check if conda env exists
conda_env_exists() {
    conda env list | grep -q "^personalparakeet "
}

# Check if we need ML support
if [ -f "config.json" ] && grep -q '"use_mock_stt": false' config.json; then
    echo "📊 Detected ML mode (use_mock_stt: false)"
    
    if conda_env_exists; then
        echo "✅ Found conda environment 'personalparakeet'"
        echo ""
        echo "🔧 To activate both environments, run these commands:"
        echo ""
        echo "   poetry shell"
        echo "   conda activate personalparakeet"
        echo ""
        echo "Then run: python main.py"
    else
        echo "❌ Conda environment 'personalparakeet' not found!"
        echo "   Run: ./install.sh and choose option 1"
    fi
else
    echo "📊 Detected Mock STT mode"
    echo ""
    echo "🔧 To activate the environment, run:"
    echo ""
    echo "   poetry shell"
    echo ""
    echo "Then run: python main.py"
fi

echo ""
echo "💡 Tip: You can also run directly with:"
echo "   poetry run python main.py"