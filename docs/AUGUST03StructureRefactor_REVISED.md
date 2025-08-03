# PersonalParakeet v3 - Modern Python Package Structure Refactoring (REVISED)

**Date**: August 3, 2025  
**Objective**: Refactor PersonalParakeet v3 to follow modern Python packaging standards  
**Impact**: Major structural changes, no functional changes  
**Package Management**: Conda/Poetry hybrid approach

## Executive Summary

PersonalParakeet v3 currently uses a flat module structure within `v3-flet/` that doesn't follow modern Python packaging best practices. This refactoring will reorganize the codebase into a proper `src/` layout with integrated ML model distribution, improving maintainability and deployment while preserving all functionality.

## Key Decisions Made

1. **ML models will be packaged with distribution** (not downloaded separately)
2. **Conda/Poetry hybrid confirmed** - Conda for ML/CUDA, Poetry for app dependencies
3. **No user migration needed** - no existing users to migrate
4. **Refactor first, test later** - focus on structure before testing

## Current Structure Analysis

### Current State (Problematic)
```
v3-flet/
├── main.py                    # Entry point at root
├── config.py                  # Configuration at root
├── audio_engine.py           # Core module at root
├── core/                     # Core functionality
│   ├── __init__.py
│   ├── stt_processor.py
│   ├── injection_manager_enhanced.py
│   ├── clarity_engine.py
│   └── ...
├── ui/                       # UI components
│   ├── __init__.py
│   ├── dictation_view.py
│   └── components.py
├── tests/                    # Tests mixed with source
├── models/                   # ML models (assumed to exist)
├── assets/                   # Static assets (if any)
├── environment.yml          # Conda environment
├── pyproject.toml           # Poetry config
└── ...
```

## Proposed Structure (Modern)

### Target State
```
PersonalParakeet/
├── src/
│   └── personalparakeet/
│       ├── __init__.py              # Package entry, version info
│       ├── __main__.py              # Entry point for python -m
│       ├── main.py                  # Application entry point
│       ├── config.py                # Configuration management
│       ├── audio_engine.py          # Audio processing engine
│       ├── core/                    # Core functionality
│       │   ├── __init__.py
│       │   ├── stt_processor.py     # Speech-to-text
│       │   ├── injection_manager_enhanced.py # Enhanced text injection
│       │   ├── clarity_engine.py    # Audio clarity
│       │   ├── vad_engine.py        # Voice activity detection
│       │   ├── application_detector.py
│       │   ├── cursor_detector.py
│       │   ├── window_detector.py
│       │   ├── thought_linker.py
│       │   └── command_processor.py
│       ├── ui/                      # User interface
│       │   ├── __init__.py
│       │   ├── dictation_view.py    # Main UI view
│       │   ├── components.py        # UI components
│       │   └── theme.py            # UI theming
│       ├── models/                  # ML models (packaged)
│       │   ├── __init__.py
│       │   ├── stt_model.onnx      # STT model file
│       │   ├── vad_model.pt        # VAD model file
│       │   └── model_config.json   # Model configurations
│       ├── assets/                  # Static assets (packaged)
│       │   ├── __init__.py
│       │   ├── icon.png
│       │   └── sounds/
│       └── utils/                   # Utility functions
│           ├── __init__.py
│           └── helpers.py           # (Currently empty - for future utility functions)
├── tests/                           # Test suite (outside src/)
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_audio_engine.py
│   ├── test_core/
│   ├── test_ui/
│   └── integration/
├── docs/                           # Documentation
├── scripts/                        # Utility scripts
├── environment.yml                # Conda environment definition
├── pyproject.toml                 # Poetry packaging config
├── README.md
├── CLAUDE.md
└── CHANGELOG.md
```

## Migration Plan

### Phase 1: Structure Creation
1. **Create src/ layout**
   ```bash
   mkdir -p src/personalparakeet/{core,ui,utils,models,assets}
   touch src/personalparakeet/__init__.py
   touch src/personalparakeet/__main__.py
   ```

2. **Initialize package files**
   ```python
   # src/personalparakeet/__init__.py
   """PersonalParakeet - Real-time dictation system."""
   __version__ = "3.0.0"
   
   # src/personalparakeet/__main__.py
   """Entry point for python -m personalparakeet."""
   from personalparakeet.main import main
   
   if __name__ == "__main__":
       main()
   ```

### Phase 2: Module Migration
1. **Copy and update core modules**
   - Move `main.py` → `src/personalparakeet/main.py`
   - Move `config.py` → `src/personalparakeet/config.py`
   - Move `audio_engine.py` → `src/personalparakeet/audio_engine.py`
   - Move `core/*` → `src/personalparakeet/core/`
   - Move `ui/*` → `src/personalparakeet/ui/`
   - Move `models/*` → `src/personalparakeet/models/`
   - Move `assets/*` → `src/personalparakeet/assets/`
   
   **Note**: Use `injection_manager_enhanced.py` as the primary injection manager. The older `injection_manager.py` can be archived.

2. **Fix import statements**
   ```python
   # OLD (problematic)
   from audio_engine import AudioEngine
   from core.stt_processor import STTProcessor
   
   # NEW (proper)
   from personalparakeet.audio_engine import AudioEngine
   from personalparakeet.core.stt_processor import STTProcessor
   ```

3. **Update resource access patterns**
   ```python
   # For ML models (package resources)
   from importlib import resources
   import personalparakeet.models
   
   # Load model from package
   with resources.files('personalparakeet.models').joinpath('stt_model.onnx').open('rb') as f:
       model_data = f.read()
   
   # For user config/logs (user directory)
   from pathlib import Path
   config_dir = Path.home() / ".personalparakeet"
   config_dir.mkdir(exist_ok=True)
   config_path = config_dir / "config.json"
   log_path = config_dir / "personalparakeet.log"
   ```

### Phase 3: Configuration Updates

1. **Update pyproject.toml**
   ```toml
   [tool.poetry]
   name = "personalparakeet"
   version = "3.0.0"
   description = "Real-time dictation system with transparent floating UI"
   authors = ["PersonalParakeet Team"]
   readme = "README.md"
   packages = [{include = "personalparakeet", from = "src"}]
   include = [
       "src/personalparakeet/models/*.onnx",
       "src/personalparakeet/models/*.pt",
       "src/personalparakeet/models/*.json",
       "src/personalparakeet/assets/**/*"
   ]
   
   [tool.poetry.dependencies]
   python = "^3.11"
   flet = "^0.28.3"
   sounddevice = "^0.4.6"
   numpy = "^1.24.0"
   scipy = "^1.10.0"
   soundfile = "^0.12.0"
   pyaudio = "^0.2.11"
   python-dotenv = "^1.0.0"
   dataclasses-json = "^0.6.0"
   keyboard = "^0.13.5"
   pynput = "^1.8.1"
   pyperclip = "^1.9.0"
   networkx = "^3.5"
   
   [tool.poetry.group.dev.dependencies]
   pytest = "^7.0.0"
   pytest-asyncio = "^0.21.0"
   pytest-cov = "^4.0.0"
   black = "^23.0.0"
   isort = "^5.12.0"
   flake8 = "^6.0.0"
   mypy = "^1.0.0"
   
   [tool.poetry.scripts]
   personalparakeet = "personalparakeet.main:main"
   
   [build-system]
   requires = ["poetry-core"]
   build-backend = "poetry.core.masonry.api"
   ```

2. **Move environment.yml to root**
   - Copy `v3-flet/environment.yml` → `environment.yml`
   - No changes needed to content

### Phase 4: Development Workflow Updates

1. **Update development setup instructions**
   ```bash
   # Clone repository
   git clone <repo>
   cd PersonalParakeet
   
   # Create conda environment with ML dependencies
   conda env create -f environment.yml
   conda activate personalparakeet
   
   # Install application with Poetry
   poetry install
   
   # Run application
   poetry run personalparakeet
   # or
   python -m personalparakeet
   ```

2. **Update CLAUDE.md commands**
   ```bash
   # OLD
   cd v3-flet/
   poetry install --with ml
   poetry run python main.py
   
   # NEW
   conda activate personalparakeet
   poetry install
   poetry run personalparakeet
   ```

### Phase 5: Model and Asset Integration

1. **Ensure models are included in package**
   - Verify all `.onnx`, `.pt`, and config files are in `src/personalparakeet/models/`
   - Update model loading code to use `importlib.resources`
   - Test model loading from packaged distribution

2. **Package assets properly**
   - Move any icons, sounds, or other assets to `src/personalparakeet/assets/`
   - Update asset loading code to use `importlib.resources`

### Phase 6: Cleanup and Validation

1. **Remove old structure**
   ```bash
   # After validation
   git rm -r v3-flet/
   git commit -m "refactor: Remove legacy v3-flet directory after migration"
   ```

2. **Update documentation**
   - Update README.md with new structure
   - Update QUICKSTART.md with new setup instructions
   - Update DEVELOPMENT.md with new workflow
   - Update all path references in docs/

## Import Structure Changes

### Before (Current)
```python
# In v3-flet/main.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Hack!

from audio_engine import AudioEngine
from ui.dictation_view import DictationView
from core.clarity_engine import ClarityEngine
```

### After (Modern)
```python
# In src/personalparakeet/main.py
from personalparakeet.audio_engine import AudioEngine
from personalparakeet.ui.dictation_view import DictationView
from personalparakeet.core.clarity_engine import ClarityEngine
```

## Development Commands

### Before
```bash
cd v3-flet/
poetry run python main.py
poetry run pytest
```

### After
```bash
# From any directory
conda activate personalparakeet
poetry run personalparakeet
poetry run pytest
python -m personalparakeet
```

## Benefits

1. **Standards Compliance**: Follows PEP 517/518 and modern packaging
2. **ML Model Distribution**: Models packaged with application
3. **Clean Imports**: No sys.path hacks
4. **Conda/Poetry Synergy**: Best of both worlds for ML and app dependencies
5. **Professional Structure**: Ready for distribution

## Risk Mitigation

1. **Gradual Migration**: Test each component after migration
2. **Version Control**: Use feature branch for all changes
3. **Validation Points**: Test functionality at each phase
4. **Rollback Ready**: Keep v3-flet/ until fully validated

## Timeline (Realistic)

### Session 1: Foundation
- [x] Create detailed plan
- [ ] Create feature branch
- [ ] Set up src/ structure
- [ ] Create package initialization files

### Session 2: Core Migration
- [ ] Migrate all Python modules
- [ ] Update all imports
- [ ] Migrate ML models and assets
- [ ] Update configuration files

### Session 3: Integration & Cleanup
- [ ] Update development workflow
- [ ] Test end-to-end functionality
- [ ] Update documentation
- [ ] Remove legacy structure

## Success Criteria

1. **Application runs** with `poetry run personalparakeet`
2. **ML models load** from package resources
3. **No import errors** or path issues
4. **Clean package structure** following standards
5. **Development workflow** uses conda + poetry seamlessly

---

**Next Steps**: Begin implementation following this revised plan, starting with creating the src/ structure and package initialization files.