# PersonalParakeet v3 - Dependency Resolution Plan

## Executive Summary

PersonalParakeet is currently in a broken state due to a fundamental dependency conflict between `nemo-toolkit` (requiring `packaging <25.0`) and the project's specification of `packaging ^25.0`. This plan provides multiple resolution strategies with step-by-step implementation guides to restore functionality while maintaining the project's hybrid dependency management approach.

**Root Cause**: Attempting to consolidate ML dependencies into Poetry exposed version conflicts that the hybrid approach was designed to avoid.

**Recommended Solution**: Return to the documented hybrid approach - Poetry for non-ML dependencies, pip for ML stack.

---

## 1. Current State Analysis

### 1.1 Immediate Conflict

```
nemo-toolkit[asr] ^2.4.0
  └── lightning >2.2.1,<=2.4.0
      └── packaging >=20.0,<25.0  ❌ CONFLICTS WITH
            personalparakeet
              └── packaging ^25.0
```

### 1.2 Recent Changes That Broke The System

Based on git status and file analysis:
1. **PyTorch added to Poetry**: Lines 31-38 in pyproject.toml show PyTorch dependencies were moved from requirements.txt into Poetry
2. **Poetry sources added**: Custom PyTorch indices were configured (lines 16-24)
3. **packaging upgraded**: Changed from compatible version to ^25.0
4. **poetry.lock invalidated**: Lock file became out of sync with these changes

### 1.3 Actual Dependency Usage

Analyzing the codebase reveals actual imports:

| Package | Used In | Required For |
|---------|---------|--------------|
| **flet** | main.py, dictation_view.py | UI Framework (ESSENTIAL) |
| **numpy** | audio_engine.py, audio_resampler.py | Audio processing (ESSENTIAL) |
| **scipy** | audio_resampler.py | Audio resampling (ESSENTIAL) |
| **sounddevice** | tests/utilities/*.py | Audio capture (ESSENTIAL) |
| **torch** | stt_processor.py | ML inference (ML-ONLY) |
| **nemo** | stt_processor.py | STT models (ML-ONLY) |
| **hydra/omegaconf** | Config loading | Config system (ESSENTIAL) |
| **pyperclip** | injection_manager.py | Text injection (ESSENTIAL) |
| **keyboard/pynput** | injection_manager.py | Input handling (ESSENTIAL) |
| **packaging** | dependency_validation.py | Version checks (OPTIONAL) |
| **networkx** | thought_linker.py | Graph algorithms (OPTIONAL) |
| **cython** | Not directly imported | Build optimization (OPTIONAL) |

---

## 2. Solution Options

### Option 1: Minimal Poetry Approach (RECOMMENDED) ✅

**Strategy**: Keep only non-ML dependencies in Poetry, manage ML stack entirely via pip/conda.

**Pros**:
- Immediate fix (< 5 minutes)
- Follows documented approach
- No version conflicts
- Proven to work

**Cons**:
- Two-step installation
- Requires documentation

**Implementation**:
1. Remove all ML dependencies from pyproject.toml
2. Keep them in requirements-ml.txt
3. Regenerate poetry.lock
4. Install in sequence: Poetry → PyTorch → ML deps

### Option 2: Version Downgrade Approach ⚠️

**Strategy**: Downgrade packaging to <25.0 to satisfy NeMo.

**Pros**:
- Single package manager
- Simpler for new developers

**Cons**:
- Limits future updates
- May break other dependencies
- Still requires PyTorch special handling

### Option 3: Full Separation Approach 🤔

**Strategy**: Create separate virtual environments for UI and ML.

**Pros**:
- Complete isolation
- No conflicts possible

**Cons**:
- Complex IPC needed
- Against single-process architecture
- Deployment nightmare

### Option 4: Docker Approach 🐳

**Strategy**: Containerize with NVIDIA Container Toolkit.

**Pros**:
- Reproducible environment
- No local conflicts

**Cons**:
- Requires Docker knowledge
- Larger deployment size
- GPU passthrough complexity

### Option 5: Modern Tool Approach 🚀

**Strategy**: Migrate to `uv` or `rye` which handle complex dependencies better.

**Pros**:
- Better dependency resolver
- Faster installation
- Modern tooling

**Cons**:
- Learning curve
- Less ecosystem support
- Migration effort

---

## 3. Recommended Implementation Plan

### Phase 1: Immediate Recovery (5 minutes)

**Step 1: Apply the following changes to pyproject.toml**

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -13,24 +13,6 @@
     "src/personalparakeet/assets/**/*"
 ]
 
-# Poetry source configuration for PyTorch with CUDA 12.8
-[[tool.poetry.source]]
-name = "pytorch-cu128"
-url = "https://download.pytorch.org/whl/cu128"
-priority = "explicit"  # Only specified packages use this source
-
-[[tool.poetry.source]]
-name = "pytorch-nightly"
-url = "https://download.pytorch.org/whl/nightly/cu128"
-priority = "explicit"  # For testing bleeding-edge builds
-
 [tool.poetry.dependencies]
 python = "^3.11"
 
-# PyTorch Stack - RTX 5090 (Blackwell sm_120) Support
-# These use the explicit pytorch-cu128 source for CUDA 12.8 compatibility
-torch = { version = "2.7.0", source = "pytorch-cu128" }
-torchvision = { version = "0.22.0", source = "pytorch-cu128" }
-torchaudio = { version = "2.7.0", source = "pytorch-cu128" }
-
-# Uncomment below to use nightly builds instead
-# torch = { version = "^2.9.0.dev20250804", source = "pytorch-nightly", allow-prereleases = true }
-# torchvision = { version = "*", source = "pytorch-nightly", allow-prereleases = true }
-# torchaudio = { version = "*", source = "pytorch-nightly", allow-prereleases = true }
-
 # ML/Audio Processing Stack
 numpy = "^1.26.0"  # Pinned for PyTorch 2.7 compatibility
 scipy = "^1.11.0"
-# TEMPORARILY DISABLED - Install via requirements-ml.txt instead
-# nemo-toolkit = { version = "^2.4.0", extras = ["asr"] }
-# pytorch-lightning = "^2.0.0"
-# torchmetrics = "^0.11.0"
 hydra-core = "^1.3.2"
 omegaconf = "^2.3.0"

 # Audio I/O
 sounddevice = "^0.4.6"
 soundfile = "^0.12.0"
 pyaudio = "^0.2.11"

 # UI Framework
 flet = "^0.28.3"

 # System Integration
 python-dotenv = "^1.0.0"
 keyboard = "^0.13.5"
 pynput = "^1.8.1"
 pyperclip = "^1.9.0"

 # Data & Configuration
 dataclasses-json = "^0.6.0"
 networkx = "^3.5"
-packaging = "^24.0"  # Downgraded for NeMo compatibility
+packaging = "^24.0"  # Version constraint for compatibility
 cython = "^3.1.2"
```

**Step 2: Execute recovery commands**

```bash
# 1. Backup current broken state
cp pyproject.toml pyproject.toml.broken
cp poetry.lock poetry.lock.broken 2>/dev/null || true

# 2. Apply the diff changes to pyproject.toml
# (Apply the diff shown above manually or use patch command)

# 3. Remove and regenerate lock
rm -f poetry.lock
poetry lock --no-update

# 4. Install base dependencies
poetry install

# 5. Install ML stack separately (if needed for STT)
conda activate personalparakeet
./scripts/install-ml.sh  # See updated script below
```

### Phase 2: Verification (2 minutes)

```bash
# 1. Test imports
poetry run python -c "import flet, numpy, scipy, sounddevice; print('✅ Core deps OK')"

# 2. Test ML imports (if needed)
poetry run python -c "import torch, nemo; print('✅ ML deps OK')"

# 3. Test application startup
poetry run python -m personalparakeet --help
```

### Phase 3: Long-term Configuration (10 minutes)

1. **Update pyproject.toml with proper structure**:
```toml
[tool.poetry]
name = "personalparakeet"
version = "3.0.0"
# ... metadata ...

[tool.poetry.dependencies]
python = "^3.11"

# Audio/Scientific Core (required for all modes)
numpy = "^1.26.0"  # <2.0 for ML compatibility
scipy = "^1.11.0"
sounddevice = "^0.4.6"
soundfile = "^0.12.0"
pyaudio = { version = "^0.2.11", optional = true }

# UI Framework
flet = "^0.28.3"

# System Integration  
python-dotenv = "^1.0.0"
keyboard = "^0.13.5"
pynput = "^1.8.1"
pyperclip = "^1.9.0"

# Configuration
hydra-core = "^1.3.2"
omegaconf = "^2.3.0"
dataclasses-json = "^0.6.0"

# Optional Enhancement
networkx = { version = "^3.5", optional = true }
packaging = { version = "^24.0", optional = true }  # For version validation

[tool.poetry.extras]
windows = ["pyaudio"]
thought-linking = ["networkx"]
dev-tools = ["packaging"]

[tool.poetry.group.dev.dependencies]
# Testing
pytest = "^7.0.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.0.0"

# Code Quality
black = "^24.3.0"
isort = "^5.12.0"
ruff = "^0.8.0"
mypy = "^1.0.0"

# Development STT
openai-whisper = { version = "^20250625", optional = true }
gtts = { version = "^2.5.4", optional = true }
```

2. **Create clear installation scripts**:

`scripts/install-base.sh`:
```bash
#!/bin/bash
# Install PersonalParakeet base dependencies (UI mode)
set -euo pipefail

echo "Installing PersonalParakeet base dependencies..."
poetry install --sync
echo "✅ Base installation complete - UI mode available"
echo "   To use real STT, run: ./scripts/install-ml.sh"
```

`scripts/install-ml.sh`:
```bash
#!/bin/bash
# Install ML dependencies for real STT functionality
# This script consolidates logic from fix_ml_dependencies.sh for clarity
set -euo pipefail

echo "Installing ML dependencies for STT..."
echo "=================================="

# Verify conda environment
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "❌ Error: Not in a conda environment!"
    echo "Please run: conda activate personalparakeet"
    exit 1
fi

if [ "$CONDA_DEFAULT_ENV" != "personalparakeet" ]; then
    echo "⚠️  Warning: Currently in '$CONDA_DEFAULT_ENV' environment"
    echo "Recommended: conda activate personalparakeet"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install PyTorch first (most critical component)
echo "📦 Installing PyTorch for RTX 5090..."
poetry run pip install -r requirements-torch.txt

# Install ML dependencies in specific order to avoid conflicts
echo "📦 Installing ML dependencies in correct order..."

# Critical: Install with specific versions for NeMo compatibility
echo "  - Installing numpy<2.0 (Numba compatibility)..."
poetry run pip install "numpy<2.0"

echo "  - Installing fsspec==2024.12.0 (NeMo requirement)..."
poetry run pip install --force-reinstall fsspec==2024.12.0

echo "  - Installing numba..."
poetry run pip install --force-reinstall --no-deps numba

echo "  - Installing remaining ML packages..."
poetry run pip install -r requirements-ml.txt

# Verify installation
echo ""
echo "🔍 Verifying ML installation..."
poetry run python -c "
import sys
try:
    import torch
    import nemo
    print('✅ PyTorch version:', torch.__version__)
    print('✅ CUDA available:', torch.cuda.is_available())
    if torch.cuda.is_available():
        print('✅ GPU:', torch.cuda.get_device_name(0))
    print('✅ NeMo version:', nemo.__version__)
except ImportError as e:
    print('❌ Import error:', e)
    sys.exit(1)
"

echo ""
echo "✅ ML installation complete - Real STT available"
echo "   Run: poetry run personalparakeet"
```

3. **Update documentation**:
- Add clear dependency tiers to README
- Document installation paths
- Add troubleshooting for common issues

**Note on fix_ml_dependencies.sh**: The existing `fix_ml_dependencies.sh` script contains valuable recovery logic for ML dependency conflicts. The new `install-ml.sh` script above consolidates this logic into a single authoritative installation script. Consider either:
- Removing `fix_ml_dependencies.sh` to avoid confusion, OR
- Renaming it to `recover_ml_dependencies.sh` and updating it to call `install-ml.sh`

---

## 4. Testing Plan

### 4.1 Minimal Functionality Test
```bash
# Should work with just Poetry deps
export PERSONALPARAKEET_USE_MOCK_STT=true
poetry run python -m personalparakeet
```

### 4.2 Full ML Test
```bash
# After ML installation
export PERSONALPARAKEET_USE_MOCK_STT=false
poetry run python -m personalparakeet
```

### 4.3 Component Tests
```bash
# Test each subsystem
poetry run pytest tests/unit/test_audio_engine.py -v
poetry run pytest tests/unit/test_clarity_engine.py -v
poetry run pytest tests/integration/test_full_pipeline.py -v
```

---

## 5. Rollback Procedures

If any step fails:

### Emergency Rollback
```bash
# 1. Restore original files
git checkout HEAD -- pyproject.toml poetry.lock

# 2. Clean environment
rm -rf .venv/
poetry env remove --all

# 3. Reinstall from scratch
poetry install
```

### Partial Rollback
```bash
# Just remove ML deps
poetry run pip uninstall -y torch torchvision torchaudio nemo-toolkit pytorch-lightning
```

---

## 6. Future Prevention Strategy

### 6.1 Dependency Management Rules

1. **NEVER add ML packages to Poetry**
   - PyTorch, NeMo, Lightning → requirements-ml.txt
   - They have complex, conflicting dependency graphs

2. **Version pinning strategy**
   - Poetry: Use ^ for flexibility
   - ML deps: Pin exact versions that work together

3. **Testing matrix**
   - CI should test: base install, base+ML, mock STT mode

### 6.2 Documentation Requirements

1. **Maintain dependency categories**:
   - Core (required)
   - ML (optional)
   - Dev (development only)
   - Platform-specific

2. **Update when adding deps**:
   - Document why it's needed
   - Which category it belongs to
   - Any version constraints

### 6.3 Automation

1. **Pre-commit hooks**:

Create `scripts/check_no_ml_in_poetry.sh`:
```bash
#!/bin/bash
# Pre-commit hook to prevent ML dependencies from being added to pyproject.toml
# This enforces the project's hybrid dependency management strategy.

set -euo pipefail

# ML packages that must not appear in pyproject.toml
ML_PACKAGES=(
    "torch"
    "torchvision" 
    "torchaudio"
    "nemo-toolkit"
    "pytorch-lightning"
    "lightning"
    "torchmetrics"
)

PYPROJECT_FILE="pyproject.toml"

echo "🔍 Checking for forbidden ML packages in ${PYPROJECT_FILE}..."

# Check for any ML packages in dependencies
for pkg in "${ML_PACKAGES[@]}"; do
    # Look for package definitions (handles various formats)
    if grep -qE "^\s*${pkg}\s*=" "${PYPROJECT_FILE}" || \
       grep -qE "^\s*${pkg}\s*\{" "${PYPROJECT_FILE}"; then
        echo "❌ ERROR: Found forbidden ML package '${pkg}' in ${PYPROJECT_FILE}"
        echo "   ML dependencies must be managed via:"
        echo "   - requirements-torch.txt (PyTorch stack)"
        echo "   - requirements-ml.txt (NeMo and related)"
        echo ""
        echo "   This separation is required because:"
        echo "   1. Poetry cannot resolve complex ML dependency graphs"
        echo "   2. RTX 5090 requires specific PyTorch builds"
        echo "   3. NeMo has strict version constraints"
        exit 1
    fi
done

# Also check for PyTorch sources
if grep -qE "^\[\[tool\.poetry\.source\]\]" "${PYPROJECT_FILE}" && \
   grep -qE "pytorch|torch" "${PYPROJECT_FILE}"; then
    echo "⚠️  WARNING: Found PyTorch-related source configuration"
    echo "   Consider removing custom sources for PyTorch indices"
fi

echo "✅ No forbidden ML packages found in Poetry configuration"
exit 0
```

Add to `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: check-poetry-ml-deps
        name: Prevent ML deps in Poetry
        entry: scripts/check_no_ml_in_poetry.sh
        language: script
        files: pyproject.toml
        pass_filenames: false
```

2. **CI validation**:

Create `.github/workflows/validate-deps.yml`:
```yaml
name: Validate Dependencies

on:
  pull_request:
    paths:
      - 'pyproject.toml'
      - 'poetry.lock'
      - 'requirements*.txt'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Check ML dependency separation
        run: |
          chmod +x scripts/check_no_ml_in_poetry.sh
          ./scripts/check_no_ml_in_poetry.sh
      
      - name: Validate Poetry configuration
        run: |
          pip install poetry
          poetry check
      
      - name: Test base installation
        run: |
          poetry install --only main
          poetry run python -c "import flet, numpy, scipy; print('✅ Base deps OK')"
```

3. **Dependency validation script**:

Create `scripts/validate_dependencies.py`:
```python
#!/usr/bin/env python3
"""Validate PersonalParakeet dependency configuration."""

import re
import sys
from pathlib import Path

def check_pyproject_toml():
    """Ensure ML packages are not in pyproject.toml."""
    ml_packages = {
        'torch', 'torchvision', 'torchaudio',
        'nemo-toolkit', 'pytorch-lightning', 
        'lightning', 'torchmetrics'
    }
    
    pyproject = Path('pyproject.toml')
    if not pyproject.exists():
        print("❌ pyproject.toml not found")
        return False
    
    content = pyproject.read_text()
    found_issues = []
    
    for pkg in ml_packages:
        # Check for package in dependencies
        if re.search(rf'^\s*{pkg}\s*=', content, re.MULTILINE):
            found_issues.append(f"Found {pkg} in Poetry dependencies")
    
    if found_issues:
        print("❌ ML packages found in pyproject.toml:")
        for issue in found_issues:
            print(f"   - {issue}")
        return False
    
    print("✅ No ML packages in pyproject.toml")
    return True

def check_requirements_files():
    """Ensure requirements files exist and are valid."""
    required_files = ['requirements-torch.txt', 'requirements-ml.txt']
    
    for req_file in required_files:
        path = Path(req_file)
        if not path.exists():
            print(f"❌ Missing {req_file}")
            return False
        
        # Basic validation
        content = path.read_text()
        if not content.strip():
            print(f"❌ {req_file} is empty")
            return False
    
    print("✅ Requirements files are present")
    return True

def main():
    """Run all dependency validations."""
    print("🔍 Validating PersonalParakeet dependency configuration...")
    print("-" * 50)
    
    checks = [
        check_pyproject_toml(),
        check_requirements_files(),
    ]
    
    if all(checks):
        print("\n✅ All dependency validations passed!")
        return 0
    else:
        print("\n❌ Dependency validation failed!")
        print("\nPlease ensure:")
        print("1. ML packages are in requirements-*.txt files")
        print("2. Only core packages are in pyproject.toml")
        print("3. Follow the hybrid dependency management strategy")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## 7. Alternative: Clean Slate Approach

If the above doesn't work, here's a nuclear option:

```bash
# 1. Export current dependencies
poetry export -f requirements.txt > all-deps.txt

# 2. Create new project
mkdir personalparakeet-clean
cd personalparakeet-clean
poetry init

# 3. Add dependencies one by one
poetry add numpy@"<2.0"  # Start with constrained versions
poetry add scipy
poetry add flet
# ... continue with known-good versions

# 4. Copy source code
cp -r ../PersonalParakeet/src .

# 5. Test incrementally
poetry run python -m personalparakeet
```

---

## 8. Decision Matrix

| Criterion | Option 1 (Minimal) | Option 2 (Downgrade) | Option 3 (Separate) | Option 4 (Docker) | Option 5 (Modern) |
|-----------|-------------------|---------------------|-------------------|------------------|------------------|
| Time to Fix | 5 min ✅ | 10 min | 2 hours | 4 hours | 1 day |
| Complexity | Low ✅ | Medium | High | High | Medium |
| Maintainability | High ✅ | Medium | Low | Medium | High |
| RTX 5090 Support | Yes ✅ | Maybe | Yes | Yes | Unknown |
| Team Learning | None ✅ | None | High | Medium | Medium |
| **Recommendation** | **✅ DO THIS** | ⚠️ Fallback | ❌ Avoid | 🤔 Future | 🤔 Future |

---

## Conclusion

The immediate path forward is clear:
1. **Revert to hybrid approach** (Poetry + pip)
2. **Remove ML deps from Poetry**
3. **Follow existing documentation**

This isn't a failure - it's validation that the original hybrid approach was correct. Poetry simply cannot handle the complexity of ML dependency graphs, especially with bleeding-edge GPU requirements.

The project was working with this approach, and it will work again once we stop fighting the tooling and embrace the documented solution.