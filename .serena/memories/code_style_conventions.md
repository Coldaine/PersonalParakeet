# Code Style and Conventions

## Python Style Configuration
- **Formatter**: Black with 100-character line length
- **Import Sorting**: isort with black profile
- **Type Checking**: mypy enabled (python_version = "3.11")
- **Target Version**: Python 3.11+

## Project Structure Conventions
- **Single-file approach preferred**: Keep implementations simple until proven
- **Main package**: `personalparakeet/` - all core functionality
- **Entry points**: `run_dictation.py` for direct execution, `__main__.py` for module execution
- **Testing**: Comprehensive test suite in `tests/` with minimal, integration, and manual tests

## Code Organization Patterns
- **LocalAgreement buffering**: Core differentiator - always prioritize this innovation
- **Cross-platform support**: Windows primary, Linux secondary
- **Direct NeMo integration**: Avoid wrapper layers, use direct model loading
- **Real-time processing**: Chunk-based audio with GPU acceleration

## Development Constraints
- **Windows compatibility**: All features must work on target platform
- **Direct testing preferred**: Manual verification over automated testing
- **LocalAgreement first**: Core innovation takes priority in all decisions
- **Avoid scope creep**: See docs/SCOPE_CREEP_LESSONS.md for lessons learned

## Naming Conventions
- **Files**: Snake_case (e.g., `local_agreement.py`, `cuda_fix.py`)
- **Classes**: PascalCase (e.g., `LocalAgreement`, `DictationSystem`)
- **Functions/Variables**: Snake_case
- **Constants**: UPPER_SNAKE_CASE

## Documentation Standards
- **Docstrings**: Keep concise, focus on purpose and key parameters
- **Comments**: Explain why, not what
- **README**: Maintain current status and working system confirmation
- **CLAUDE.md**: Keep updated with working system status and development constraints