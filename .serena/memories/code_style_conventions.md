# PersonalParakeet Code Style & Conventions

## Code Formatting
- **Black**: Line length 100, Python 3.11 target
- **isort**: Black profile, line length 100
- **Ruff**: Selected rules for errors, warnings, flake8-bugbear, comprehensions, pyupgrade

## Python Standards
- **Python Version**: 3.11+ (for ML compatibility)
- **Type Hints**: Required (mypy configured)
- **Docstrings**: Required for classes and public methods
- **Line Length**: 100 characters (Black standard)

## Architecture Patterns
- **Dataclass Configuration**: All config using @dataclass with dataclasses-json
- **Async/Await**: Extensive use for UI and audio processing
- **Thread Safety**: asyncio.run_coroutine_threadsafe() for cross-thread calls
- **Producer-Consumer**: queue.Queue for audio processing
- **Dependency Injection**: Components passed via constructor

## Naming Conventions
- **Classes**: PascalCase (e.g., PersonalParakeetV3, AudioEngine)
- **Methods/Functions**: snake_case (e.g., initialize, configure_window)
- **Variables**: snake_case (e.g., audio_engine, is_running)
- **Constants**: UPPER_SNAKE_CASE
- **Private Methods**: Leading underscore (_method_name)

## Error Handling
- **Comprehensive logging**: logger.info, logger.error with detailed context
- **Exception details**: Include type, args, and full traceback
- **Graceful degradation**: Emergency cleanup on failures
- **Signal handling**: SIGINT, SIGTERM for clean shutdown

## Documentation
- **Triple quotes**: \"\"\"Docstring format\"\"\"
- **Inline comments**: Explain complex logic and threading concerns
- **Type annotations**: Full type hints for all parameters and returns

## Forbidden Patterns (v3 Architecture)
- WebSocket servers/clients
- subprocess for UI components
- Multi-process architecture
- Cross-thread UI access without asyncio safety
- Mock hardware in tests (real hardware required)