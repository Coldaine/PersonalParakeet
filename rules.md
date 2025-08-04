# Dependency Management Rules

**CRITICAL: PersonalParakeet uses a hybrid conda/Poetry dependency management system. ALL agents MUST follow this exact sequence:**

```bash
# 1. ALWAYS activate conda first (system binaries, CUDA 12.8, Python 3.11)
conda activate personalparakeet

# 2. Install Poetry dependencies (pure Python packages)
poetry install

# 3. Install PyTorch for RTX 5090 (CRITICAL: must be before other ML packages)
poetry run pip install -r requirements-torch.txt

# 4. ALL subsequent commands must use Poetry's environment
poetry run <command>
```

**Why this hybrid approach exists:**
- **Conda**: Manages system binaries (CUDA drivers, audio drivers, build tools) that Poetry cannot handle
- **Poetry**: Manages pure Python dependencies with deterministic resolution and lock files
- **Requirements files**: Handle PyTorch nightly builds and complex ML dependencies that conflict with Poetry's resolver

**NEVER:**
- Run commands without `conda activate personalparakeet` first
- Skip the PyTorch installation step
- Use system pip instead of `poetry run pip`
- Install PyTorch through Poetry (it's excluded from pyproject.toml intentionally)

**If dependency issues arise:** The project includes fix scripts (`fix_ml_dependencies.sh`) and clean install procedures. Always activate conda environment before running any fix scripts.

This system prevents RTX 5090 compatibility issues and ML dependency conflicts that would otherwise break the project.