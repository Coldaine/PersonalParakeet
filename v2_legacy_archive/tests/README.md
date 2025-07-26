# PersonalParakeet Test Suite

This directory contains comprehensive unit and integration tests for the PersonalParakeet project, covering all the improvements implemented in turns 4-6.

## Test Coverage

### 1. Logger Tests (`test_logger.py`)
- Logger initialization and configuration
- Console and file handler setup
- Logging format and emoji integration
- File path generation with dates
- Prevention of duplicate handlers

### 2. Clipboard Manager Tests (`test_clipboard_managers.py`)
- Abstract base class enforcement
- Linux clipboard manager (xclip, xsel, wl-copy)
- Windows clipboard manager (win32clipboard)
- Retry logic and error handling
- Tool detection and fallback mechanisms

### 3. Configuration Tests (`test_config.py`)
- InjectionConfig dataclass functionality
- Default and custom value handling
- Immutability (frozen dataclass)
- Equality and hashing behavior
- Type annotations preservation

### 4. Windows Injection Config Tests (`test_windows_injection_config.py`)
- All Windows strategies accept InjectionConfig
- Config delays are properly used
- Default config fallback
- Config immutability across strategies
- Behavioral changes with different configs

### 5. Constants Tests (`test_constants.py`)
- LogEmoji values and uniqueness
- Platform detection constants
- String type validation
- Integration with logging context

### 6. Integration Tests (`test_text_injection_integration.py`)
- Full text injection flow
- Strategy ordering and fallback
- Platform-specific initialization
- Application-aware injection
- Special character handling
- Logging integration

## Running Tests

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Specific Test Module
```bash
# Run only logger tests
python tests/run_all_tests.py logger

# Run only clipboard tests
python tests/run_all_tests.py clipboard_managers

# Run only config tests
python tests/run_all_tests.py config
```

### Run Tests with unittest
```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_logger

# Run specific test class
python -m unittest tests.test_logger.TestLogger

# Run specific test method
python -m unittest tests.test_logger.TestLogger.test_setup_logger_creates_logger
```

### Run with pytest (if installed)
```bash
# Run all tests
pytest tests/

# Run specific file
pytest tests/test_logger.py

# Run with coverage
pytest tests/ --cov=personalparakeet
```

## Test Requirements

Some tests use mocking and don't require actual dependencies, but for full testing:

- Python 3.8+
- unittest (built-in)
- unittest.mock (built-in)
- All project dependencies from requirements.txt

## Platform-Specific Tests

- **Windows tests**: Require win32clipboard (mocked in tests)
- **Linux tests**: Check for xclip/xsel/wl-copy (mocked in tests)
- **Cross-platform**: Most tests use mocks to work on any platform

## Writing New Tests

When adding new functionality:

1. Create a test file following the pattern `test_<module_name>.py`
2. Import required modules and mocks
3. Create test classes inheriting from `unittest.TestCase`
4. Write test methods starting with `test_`
5. Use descriptive test names explaining what is being tested
6. Mock external dependencies to ensure tests are isolated

## Test Best Practices

1. **Isolation**: Each test should be independent
2. **Mocking**: Mock external dependencies (clipboard, keyboard, etc.)
3. **Coverage**: Aim for high code coverage but focus on critical paths
4. **Assertions**: Use specific assertions with clear messages
5. **Setup/Teardown**: Use setUp() and tearDown() for test preparation
6. **Documentation**: Add docstrings explaining complex test scenarios

## Continuous Integration

These tests are designed to run in CI environments:
- No GUI dependencies (all UI interactions are mocked)
- No hardware dependencies (audio, keyboard mocked)
- Platform detection is mocked for cross-platform testing
- Fast execution (< 1 second for unit tests)