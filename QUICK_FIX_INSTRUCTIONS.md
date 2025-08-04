# PersonalParakeet - Quick Fix Instructions

## Option 1: Minimal Poetry Approach (RECOMMENDED - Try This First!)

Remove ML dependencies from Poetry and manage them separately:

```bash
# 1. Edit pyproject.toml and REMOVE these sections/lines:
#    - ALL [[tool.poetry.source]] sections (lines 16-24)
#    - torch = { version = "2.7.0", source = "pytorch-cu128" }
#    - torchvision = { version = "0.22.0", source = "pytorch-cu128" }
#    - torchaudio = { version = "2.7.0", source = "pytorch-cu128" }
#    - Keep the commented nemo/pytorch-lightning lines commented

# 2. Clean and reinstall with Poetry:
rm -f poetry.lock
poetry lock
poetry install

# 3. Install ML stack separately:
conda activate personalparakeet
poetry run pip install -r requirements-torch.txt
poetry run pip install -r requirements-ml.txt

# 4. Run the app:
poetry run python -m personalparakeet
```

---

## Option 5: Modern Tool Approach with UV

Migrate from Poetry to UV (Astral's fast Python package manager):

```bash
# 1. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Create UV project structure
mkdir personalparakeet-uv
cd personalparakeet-uv

# 3. Initialize UV project
uv init

# 4. Create pyproject.toml for UV:
cat > pyproject.toml << 'EOF'
[project]
name = "personalparakeet"
version = "3.0.0"
requires-python = ">=3.11"
dependencies = [
    "numpy<2.0",
    "scipy>=1.11.0",
    "flet>=0.28.3",
    "sounddevice>=0.4.6",
    "soundfile>=0.12.0",
    "python-dotenv>=1.0.0",
    "pyperclip>=1.9.0",
    "hydra-core>=1.3.2",
    "omegaconf>=2.3.0",
    "dataclasses-json>=0.6.0",
    "keyboard>=0.13.5",
    "pynput>=1.8.1",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=24.3.0",
    "ruff>=0.8.0",
]
EOF

# 5. Install base dependencies with UV:
uv pip sync pyproject.toml

# 6. Copy your source code:
cp -r /mnt/windows_e/_projects/PersonalParakeet/src .

# 7. Install ML dependencies (UV still can't solve the ML conflicts!):
uv pip install -r /mnt/windows_e/_projects/PersonalParakeet/requirements-torch.txt
uv pip install -r /mnt/windows_e/_projects/PersonalParakeet/requirements-ml.txt

# 8. Run with UV:
uv run python -m personalparakeet
```

**Note**: UV is 10-100x faster but still hits the same ML dependency conflicts. You'd still need the hybrid approach!

---

## Quick Decision Guide

- **Want it working NOW?** → Use Option 1 (5 minutes)
- **Want to try modern tooling?** → Use Option 5 (30+ minutes, same conflicts)
- **Just want it to work on your personal machine?** → Honestly, just use Option 1

The ML dependency conflicts exist regardless of the tool. Option 1 is the fastest path to a working system.