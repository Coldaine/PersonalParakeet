# PersonalParakeet Automated Testing Guide

## Overview

PersonalParakeet uses a comprehensive automated testing strategy covering both v2 (current) and v3 (Flet refactor) implementations. This guide covers local testing, CI/CD setup, and testing best practices.

## Testing Architecture

### v2 Testing (Legacy)
- **Location**: `tests/` directory
- **Runner**: `tests/run_all_tests.py`
- **Coverage**: Unit, integration, and manual tests
- **Known Issues**: Import errors, outdated configs, missing core module tests

### v3 Testing (New Flet Implementation)
- **Location**: `v3-flet/tests/` directory  
- **Runner**: `v3-flet/run_tests.py`
- **Coverage**: Component imports, GUI launch, audio engine, integration
- **Status**: Comprehensive test suite with mocking for hardware dependencies

## Test Categories

### 1. Component Import Tests
**Purpose**: Verify all modules can be imported without errors

```bash
# v3 Test
cd v3-flet
python -m pytest tests/test_components.py -v

# v2 Test  
cd tests
python test_constants.py
```

**Covers**:
- Flet framework imports
- Core component imports (STT, Clarity, VAD)
- UI component imports
- Configuration imports

### 2. Audio Engine Tests
**Purpose**: Test audio pipeline without hardware dependencies

```bash
cd v3-flet
python -m pytest tests/test_audio_engine.py -v
```

**Features**:
- Mock audio data processing
- VAD integration testing
- STT pipeline verification
- Resource cleanup validation

### 3. Integration Tests
**Purpose**: End-to-end functionality verification

```bash
cd v3-flet
python -m pytest tests/test_integration.py -v
```

**Covers**:
- App initialization
- Component communication
- UI creation and updates
- Audio pipeline integration
- Cleanup procedures

### 4. GUI Launch Tests
**Purpose**: Verify GUI can start without user interaction

```bash
cd v3-flet
python tests/test_gui_launch.py
```

**Features**:
- Headless GUI testing
- Window configuration
- Component initialization
- Error handling

## Local Testing

### Quick Test Suite (v3)
```bash
cd v3-flet
python run_tests.py
```

**Output Format**:
```
🔧 Running Component Import Test...
✓ flet_imports: PASS
✓ config_imports: PASS
✓ core_imports: PASS
✓ ui_imports: PASS

🚀 Running GUI Launch Test...
✓ gui_launch: PASS

🎵 Running Audio Engine Test...
✓ initialization: PASS
✓ mock_audio_processing: PASS

🔗 Running Integration Test...
✓ app_initialization: PASS
✓ component_integration: PASS

OVERALL: ALL TESTS PASSED
```

### Comprehensive Test Suite (v2)
```bash
cd tests
python run_all_tests.py
```

### Individual Test Categories
```bash
# Unit tests
python -m pytest tests/unit/ -v

# Integration tests  
python -m pytest tests/integration/ -v

# Manual tests (require user interaction)
python tests/manual/test_audio_device_selection.py
```

## CI/CD Testing

### GitHub Actions Workflows

#### Test Pipeline (`test.yml`)
**Triggers**: Push to main/develop/flet-v3-refactor, PRs to main

**Jobs**:
1. **test-v2**: Ubuntu testing of v2 components
2. **test-v3**: Ubuntu testing of v3 Flet implementation  
3. **test-windows**: Windows compatibility testing
4. **lint-and-format**: Code quality checks (flake8, black, isort)
5. **security-scan**: Security analysis (bandit, safety)
6. **integration-smoke-test**: Cross-version validation

#### Deploy Pipeline (`deploy.yml`)
**Triggers**: Version tags, releases, manual dispatch

**Jobs**:
1. **build-v3-executable**: PyInstaller Windows executable
2. **build-v2-package**: Python package distribution
3. **create-release**: GitHub release with artifacts
4. **deploy-docs**: Documentation deployment

### Setting Up CI/CD

1. **Enable GitHub Actions**:
   ```bash
   # Workflows are automatically detected in .github/workflows/
   git add .github/workflows/
   git commit -m "Add automated testing workflows"
   git push origin main
   ```

2. **Configure Branch Protection**:
   - Go to repository Settings → Branches
   - Add rule for `main` branch
   - Require status checks: "Test v2 Components", "Test v3 Flet Implementation"
   - Require branches to be up to date

3. **Set up Secrets** (if needed):
   - `GITHUB_TOKEN`: Automatically provided
   - Additional secrets for external services

## Testing Best Practices

### Writing New Tests

#### Test Structure
```python
#!/usr/bin/env python3
"""
Test Description for PersonalParakeet v3
Brief description of what this test covers
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YourTest:
    def __init__(self):
        self.test_results = {
            'test_1': False,
            'test_2': False,
            'total_errors': 0
        }
    
    def test_something(self):
        try:
            # Test implementation
            logger.info("✓ Test passed")
            self.test_results['test_1'] = True
            return True
        except Exception as e:
            logger.error(f"✗ Test failed: {e}")
            self.test_results['total_errors'] += 1
            return False
```

#### Mocking Hardware Dependencies
```python
from unittest.mock import Mock, patch, AsyncMock

# Mock audio hardware
with patch('sounddevice.query_devices'), \
     patch('sounddevice.default'), \
     patch('torch.cuda.is_available', return_value=True):
    
    # Your test code here
    pass
```

### Test Coverage Guidelines

**Must Test**:
- All public APIs
- Error handling paths
- Resource cleanup
- Hardware abstraction layers

**Should Test**:
- Integration between components
- Configuration validation
- UI responsiveness

**Can Skip**:
- External library functionality
- Platform-specific details (when mocked)
- Third-party model inference (mock the results)

## Debugging Test Failures

### Common Issues

#### Import Errors
```bash
# Check Python path
python -c "import sys; print('\\n'.join(sys.path))"

# Verify module structure
ls -la personalparakeet/
ls -la v3-flet/core/
```

#### Hardware Dependencies
```bash
# Check if tests are properly mocked
grep -r "sounddevice" tests/
grep -r "@patch" tests/
```

#### Async Test Issues
```bash
# Ensure proper async test setup
python -c "import asyncio; print(asyncio.get_event_loop())"
```

### Debugging Commands

```bash
# Run with verbose output
python -m pytest tests/ -v -s

# Run specific test with debugging
python -m pytest tests/test_audio_engine.py::AudioEngineTest::test_initialization -v -s

# Run with coverage report
pip install pytest-cov
python -m pytest tests/ --cov=personalparakeet --cov-report=html
```

## Test Maintenance

### Updating Tests After Code Changes

1. **Import Changes**: Update `test_components.py`
2. **API Changes**: Update integration tests
3. **New Features**: Add corresponding test cases
4. **Deprecations**: Mark tests as deprecated, don't remove immediately

### Test Performance

**Target Metrics**:
- Complete test suite: < 2 minutes
- Individual test: < 30 seconds
- Import tests: < 5 seconds

**Optimization**:
- Use mocks for expensive operations
- Cache test fixtures when possible
- Run tests in parallel where safe

## Continuous Improvement

### Test Quality Metrics

Track these metrics over time:
- Test coverage percentage
- Test execution time
- Flaky test frequency
- CI/CD success rate

### Regular Reviews

**Monthly**: Review test coverage reports
**Per Release**: Update test cases for new features
**After Incidents**: Add regression tests

## Troubleshooting

### GitHub Actions Failures

1. **Check workflow logs** in GitHub Actions tab
2. **Verify dependencies** are correctly specified
3. **Test locally** with same Python version
4. **Check branch protection** rules

### Local Test Environment

```bash
# Reset test environment
rm -rf __pycache__/ .pytest_cache/
python -m pip install --force-reinstall -r requirements.txt

# Clear previous test artifacts  
rm -f test_results_*.json
rm -f *.log
```

This comprehensive testing setup ensures PersonalParakeet maintains high quality and reliability across both v2 and v3 implementations while supporting continuous integration and deployment workflows.