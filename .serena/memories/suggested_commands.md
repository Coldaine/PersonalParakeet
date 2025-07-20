# Suggested Commands for PersonalParakeet

## Virtual Environment Setup (CRITICAL ISSUE IDENTIFIED)
```powershell
# Current Issue: Python version mismatch (3.11.9 in venv vs 3.13.5 system)
# Solution: Recreate virtual environment with correct Python version

# Remove corrupted venv
Remove-Item -Recurse -Force .venv

# Create new venv with Python 3.11
C:\Program Files\Python311\python.exe -m venv .venv

# Activate venv
.venv\Scripts\activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Core Development Commands
```bash
# Run the working dictation system
python run_dictation.py

# Test critical components
python tests/test_audio_minimal.py      # Windows audio capture test
python tests/test_local_agreement.py    # LocalAgreement buffer test
python tests/test_keyboard_output.py    # Cross-platform keyboard output test

# Install as package and run
pip install -e .
personalparakeet
```

## Development & Testing
```bash
# Run comprehensive test suite
python run_all_tests.py

# Individual component testing
python tests/test_dictation.py
python tests/test_audio_minimal.py

# GPU monitoring (essential for performance)
nvidia-smi
# For continuous monitoring:
# powershell: while($true) { nvidia-smi; Start-Sleep 1; Clear-Host }
```

## Package Management
```bash
# Update requirements after installing new packages
pip freeze > requirements.txt

# Code formatting (if dev dependencies installed)
black --line-length 100 .
isort --profile black .

# Type checking
mypy personalparakeet/
```

## Windows-Specific Commands
```powershell
# Check Python versions available
where python
python --version

# PowerShell directory listing
Get-ChildItem -Force

# Test audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"
```