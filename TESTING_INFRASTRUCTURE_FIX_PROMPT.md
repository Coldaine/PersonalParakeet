# Testing Infrastructure Fix - Agent Prompt

## Task Overview
Fix the testing infrastructure for the PersonalParakeet repository to get all CI checks passing. The main application functionality is working correctly, but the testing pipeline has multiple pre-existing issues that need to be resolved.

## Repository Context
- **Repository**: Coldaine/PersonalParakeet  
- **PR to Fix**: #10 (https://github.com/Coldaine/PersonalParakeet/pull/10)
- **Branch**: devin/1754552184-rust-gui-cleanup
- **Latest Commit**: 03be44b

## Current CI Status
All 8 CI checks are failing, but the failures are primarily due to pre-existing testing infrastructure issues, not the recent Rust GUI migration cleanup work.

## Issues Already Fixed
The following issues have been successfully resolved:
1. ✅ Trailing whitespace in `thought_linker.py` 
2. ✅ CI workflow test directory paths (corrected from `tests/test_core/` to `tests/core/` and `tests/unit/`)
3. ✅ ML dependency installation steps added to CI workflow
4. ✅ Black formatting syntax errors resolved

## Remaining CI Failures to Fix

### 1. Import Sorting (isort) - 48+ Files Affected
**Issue**: Widespread import sorting violations across the codebase
**Files**: 48+ files including `config.py`, `main.py`, `audio_engine.py`, and many others
**Error**: `ERROR: Imports are incorrectly sorted and/or formatted`
**Solution**: Run `isort --profile black src/personalparakeet/ tests/` to fix all import sorting issues

### 2. Test Collection/Execution Issues
**Issue**: Tests are being collected but then deselected, causing exit code 5
**Symptoms**: 
- `collecting ... collected 15 items / 15 deselected / 0 selected`
- `Process completed with exit code 5`
**Root Cause**: Tests don't have proper pytest markers for the CI filter `-m "unit and not slow"`
**Files to Check**: 
- `tests/unit/test_config.py` - uses `unittest.TestCase` but no pytest markers
- `tests/unit/test_thought_linker.py` - uses `unittest.TestCase` but no pytest markers

### 3. PyTorch Dependency Issues (macOS)
**Issue**: CI trying to install non-existent PyTorch version
**Error**: `ERROR: Could not find a version that satisfies the requirement torch>=2.9.0.dev20250804`
**File**: `requirements-torch.txt` line 11
**Solution**: Update to available PyTorch nightly version or use stable release

### 4. Coverage Report Failures
**Issue**: Coverage combination failing due to no test data
**Error**: `No data to combine`
**Root Cause**: Downstream effect of test execution failures

### 5. TestReporter Collection Warnings
**Issue**: pytest collection warnings for TestReporter class
**Error**: `PytestCollectionWarning: cannot collect test class 'TestReporter' because it has a __init__ constructor`
**File**: `tests/core/test_reporter.py`
**Solution**: Rename class to avoid pytest collection or add `__test__ = False`

## Technical Details

### Test Marker Issues
The unit tests use `unittest.TestCase` but don't have pytest markers:
```python
# Current (problematic):
class TestConfig(unittest.TestCase):
    def test_default_config_loading(self):
        # ...

# Needs pytest markers:
import pytest

class TestConfig(unittest.TestCase):
    @pytest.mark.unit
    def test_default_config_loading(self):
        # ...
```

### Import Sorting Examples
Example from `config.py`:
```python
# Current (incorrect):
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
import logging
import json

# Should be (isort --profile black):
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
```

### PyTorch Version Issue
`requirements-torch.txt` specifies:
```
torch>=2.9.0.dev20250804
```
But available versions only go up to 2.8.0 in the nightly index.

## Recommended Fix Approach

### Phase 1: Import Sorting (Quick Win)
```bash
cd /path/to/PersonalParakeet
poetry run isort --profile black src/personalparakeet/ tests/
git add -A
git commit -m "fix: Resolve import sorting issues across codebase"
```

### Phase 2: Test Markers
Add `@pytest.mark.unit` to all unit tests in:
- `tests/unit/test_config.py`
- `tests/unit/test_thought_linker.py`
- Any other unit test files

### Phase 3: PyTorch Dependencies
Update `requirements-torch.txt` to use available versions:
```
torch>=2.8.0
torchvision>=0.19.0
torchaudio>=2.8.0
```

### Phase 4: TestReporter Collection Issue
Fix the TestReporter class collection warning by adding:
```python
class TestReporter:
    __test__ = False  # Tell pytest not to collect this as a test class
```

### Phase 5: Verification
```bash
# Test locally before pushing:
poetry run black --check --diff src/personalparakeet/ tests/
poetry run isort --check-only --diff src/personalparakeet/ tests/
pytest tests/core/ tests/unit/ -m "unit and not slow" --collect-only
pytest tests/core/ tests/unit/ -m "unit and not slow" -v
```

## Success Criteria
- All 8 CI checks pass
- Tests execute successfully (no more "15 deselected / 0 selected")
- Import sorting passes
- PyTorch dependencies install on all platforms
- Coverage reports generate successfully

## Important Notes
- The main application functionality is working correctly
- The Rust GUI migration cleanup is complete and functional
- These are pre-existing testing infrastructure issues, not application bugs
- Focus on getting CI passing, not changing application logic
- Test all fixes locally before pushing to avoid CI iteration delays

## Files to Modify
1. All files with isort violations (run isort to identify)
2. `tests/unit/test_config.py` - add pytest markers
3. `tests/unit/test_thought_linker.py` - add pytest markers  
4. `requirements-torch.txt` - update PyTorch versions
5. `tests/core/test_reporter.py` - fix collection warning
6. Any other unit test files missing pytest markers

## Repository Setup
```bash
git clone https://github.com/Coldaine/PersonalParakeet.git
cd PersonalParakeet
git checkout devin/1754552184-rust-gui-cleanup
poetry install
```

The repository uses Poetry for dependency management and has a Rust component that compiles automatically during installation.

## Context About Previous Work
The Rust GUI migration cleanup work has been completed successfully. The main application now uses `personalparakeet_ui.GuiController()` from Rust instead of the old Flet-based Python GUI. The cleanup removed:
- Non-functional entry points (`__main__.py`)
- Unused Flet-based code remnants
- Updated documentation to reflect Rust UI architecture

The CI failures are unrelated to this cleanup work and are pre-existing testing infrastructure issues that need to be resolved to get the PR merged.
