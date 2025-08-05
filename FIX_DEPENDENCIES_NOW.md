# Fix PersonalParakeet Dependencies - START HERE

## The Problem
ALL recent commits have PyTorch in Poetry, which causes unsolvable dependency conflicts with nemo-toolkit. The hybrid approach (Poetry for core, pip for ML) has never been properly implemented in git history.

## Quick Fix Steps

### Step 1: Clean pyproject.toml Manually

Since no previous commit has the correct setup, we need to fix it manually:

```bash
# Edit pyproject.toml and REMOVE:
# 1. Delete ALL [[tool.poetry.source]] sections (lines with pytorch URLs)
# 2. Delete torch = ..., torchvision = ..., torchaudio = ... lines
# 3. Delete OR comment out nemo-toolkit, pytorch-lightning, torchmetrics lines
# 4. Change packaging = "^25.0" to packaging = "^24.0" if present
```

### Step 2: Clean and Reinstall

```bash
# Remove broken lock file
rm -f poetry.lock

# Generate fresh lock file
poetry lock

# Install base dependencies
poetry install
```

### Step 3: Install ML Dependencies

```bash
# Make sure conda is active
conda activate personalparakeet

# Install PyTorch for RTX 5090
poetry run pip install -r requirements-torch.txt

# Install ML stack (NeMo, etc.)
poetry run pip install -r requirements-ml.txt
```

### Step 4: Test

```bash
# Should work now!
poetry run python -m personalparakeet
```

## If You Want to Try UV Instead

First fix the immediate issue with the steps above, THEN consider UV:

```bash
# Install UV
pip install uv

# Create new project with UV
uv init personalparakeet-uv
cd personalparakeet-uv

# Copy your source files
cp -r ../PersonalParakeet/src .
cp ../PersonalParakeet/requirements-*.txt .

# Install with UV
uv pip install -r requirements-base.txt
uv pip install -r requirements-torch.txt --index-url https://download.pytorch.org/whl/cu128
uv pip install -r requirements-ml.txt
```

But honestly? Just do the revert first. You can explore UV later when things are working.