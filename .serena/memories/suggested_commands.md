# PersonalParakeet Development Commands

## ⚠️ CRITICAL: Environment Setup
**ALWAYS run conda activate first before ANY other command!**
```bash
# REQUIRED FIRST STEP - Must activate conda environment
conda activate personalparakeet
```

## Installation & Dependencies
```bash
# Install application dependencies
poetry install

# Install PyTorch with RTX 5090 support
poetry run pip install -r requirements-torch.txt

# Install ML dependencies (NeMo, etc.)
poetry run pip install -r requirements-ml.txt

# Clean ML dependency install (if issues)
./fix_ml_dependencies.sh
```

## Running the Application
```bash
# Primary run command
poetry run personalparakeet

# Alternative run command
python -m personalparakeet

# Background run (if script exists)
python run_background.py
```

## Testing Commands
```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest -m unit                    # Unit tests
poetry run pytest -m integration            # Integration tests
poetry run pytest -m hardware               # Hardware tests
poetry run pytest -m interactive            # Interactive tests

# Run specific test files
poetry run pytest tests/integration/test_full_pipeline.py
poetry run pytest tests/hardware/test_audio_capture.py

# Run tests with verbose output
poetry run pytest -v --tb=short
```

## Code Quality & Formatting
```bash
# Format code with Black
poetry run black . --line-length 100

# Sort imports with isort
poetry run isort . --profile black

# Lint with Ruff
poetry run ruff check .
poetry run ruff check . --fix          # Auto-fix issues

# Type checking with MyPy
poetry run mypy .

# Run all quality checks
poetry run black . --line-length 100 && poetry run isort . --profile black && poetry run ruff check . && poetry run mypy .
```

## Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## Debugging & Diagnostics
```bash
# Check ML stack compatibility
poetry run python -c "import torch; import torchvision; import torchaudio; print('✅ PyTorch OK')"
poetry run python -c "import nemo.collections.asr as nemo_asr; print('✅ NeMo OK')"

# Validate environment
python validate_environment.py
./validate_environment.sh

# Check GPU availability
python gpu_test.py

# Check dependencies
python check_dependencies.py
```

## System Utilities (Linux)
```bash
# Standard Linux commands available
ls -la                    # List files with details
find . -name "*.py"       # Find Python files
grep -r "pattern" src/    # Search in source code
ps aux | grep python      # Check running Python processes
kill -9 <pid>            # Force kill process
df -h                    # Check disk space
free -h                  # Check memory usage
```