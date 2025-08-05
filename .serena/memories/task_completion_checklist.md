# PersonalParakeet Task Completion Checklist

## ⚠️ CRITICAL: Pre-Command Setup
**ALWAYS activate conda environment first:**
```bash
conda activate personalparakeet
```

## Code Quality Checks (REQUIRED)
When any code changes are made, run these commands in order:

```bash
# 1. Format code
poetry run black . --line-length 100

# 2. Sort imports
poetry run isort . --profile black

# 3. Lint and fix issues
poetry run ruff check . --fix

# 4. Type checking
poetry run mypy .
```

## Testing Requirements
- **Hardware Tests Required**: All tests use real hardware (no mocks)
- **Integration Tests**: Must run end-to-end tests for STT pipeline
- **Test Commands**:
```bash
# Run relevant tests
poetry run pytest tests/unit/           # Unit tests
poetry run pytest tests/integration/    # Integration tests
poetry run pytest tests/hardware/       # Hardware validation

# For ML/STT changes, specifically run:
poetry run pytest tests/integration/test_full_pipeline.py
```

## Dependency Validation
After ML dependency changes:
```bash
# Verify PyTorch imports
poetry run python -c "import torch; import torchvision; import torchaudio; print('✅ PyTorch OK')"

# Verify NeMo imports
poetry run python -c "import nemo.collections.asr as nemo_asr; print('✅ NeMo OK')"

# Run full ML stack check
python validate_environment.py
```

## Pre-commit Validation
```bash
# Run pre-commit hooks
pre-commit run --all-files
```

## Documentation Updates
- Update relevant .md files in docs/ if architecture changes
- Update CLAUDE.md if command changes affect future AI interactions
- Update STATUS.md progress tracking if significant features completed

## ❌ NEVER COMMIT WITHOUT:
1. Conda environment activated
2. All quality checks passing
3. Relevant tests passing
4. Pre-commit hooks passing
5. ML dependencies validated (for ML changes)

## Architecture Compliance Check
Ensure no forbidden patterns were introduced:
- ❌ WebSocket servers/clients
- ❌ subprocess for UI
- ❌ Multi-process architecture
- ❌ Cross-thread UI access without asyncio safety
- ❌ Mock hardware tests