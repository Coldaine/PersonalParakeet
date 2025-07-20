# Python 3.11 Migration Plan for PersonalParakeet

## Overview
Migrate PersonalParakeet from Python 3.13 to Python 3.11 to resolve NeMo toolkit compatibility issues with RTX 5090.

**Note**: Python 3.11 is the recommended version for ML/AI projects as of 2025. Most data science libraries have stable support for 3.11, while newer versions (3.12+) often have compatibility issues. We'll stay on 3.11 until the ecosystem fully supports newer versions (typically 6-12 months after release).

## Steps

### 1. Uninstall Python 3.13
- Open Windows Settings → Apps → Installed apps
- Search for "Python 3.13"
- Click the three dots → Uninstall
- Follow the uninstall wizard

### 2. Install Python 3.11
- Download Python 3.11.9 from [python.org](https://www.python.org/downloads/release/python-3119/)
- During installation:
  - ✅ Check "Add Python 3.11 to PATH"
  - ✅ Check "Install for all users"
  - ✅ Check "Install launcher for all users"

### 3. Remove Old Virtual Environment
```bash
# In PowerShell, from project root:
Remove-Item -Recurse -Force .venv
```

### 4. Create New Virtual Environment with Python 3.11
```bash
# Since 3.11 is now the only Python installed:
python -m venv .venv
```

### 5. Activate and Install Dependencies
```bash
# Activate virtual environment
.venv\Scripts\activate

# Install PyTorch nightly for RTX 5090 (CUDA 12.8+)
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# Install core dependencies
pip install sounddevice keyboard

# Install NeMo toolkit
pip install nemo_toolkit[asr]

# Install additional dependencies
pip install pytest pytest-asyncio pytest-mock
```

### 6. Verify Installation
```bash
# Test Python version
python --version  # Should show 3.11.x

# Test RTX 5090 compatibility
python test_rtx5090.py

# Test audio system
python tests/manual/test_audio_minimal.py

# Run dictation system
python -m personalparakeet
```

## Expected Outcome
- Python 3.11 environment with full NeMo compatibility
- RTX 5090 working with PyTorch nightly (CUDA 12.8)
- PersonalParakeet dictation system fully functional
- Stable environment that won't break with ecosystem updates

## Benefits of This Approach
- **Simplicity**: Only one Python version to manage
- **No confusion**: `python` always means Python 3.11
- **Clean system**: No version conflicts or PATH issues
- **Industry standard**: Following ML/AI best practices

## Long-term Strategy
- **Stay on Python 3.11** throughout 2025
- **Reevaluate in Q3 2025** when Python 3.13 ecosystem matures
- **Monitor NeMo releases** for official Python 3.12+ support
- **Follow the "6-month rule"** - wait for ecosystem stability before upgrading