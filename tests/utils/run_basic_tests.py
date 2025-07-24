#!/usr/bin/env python3
"""Run tests that don't require external dependencies"""

import unittest
import sys
import os

# Add parent directory to path
# Now we need to go up two levels since we're in tests/utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Only run tests that don't require external dependencies
BASIC_TESTS = [
    'test_config',
    'test_constants',
]

def run_basic_tests():
    """Run only tests that don't require external dependencies"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Get the tests directory
    test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    unit_dir = os.path.join(test_dir, 'unit')
    
    # Add unit directory to path
    sys.path.insert(0, unit_dir)
    
    for test_name in BASIC_TESTS:
        try:
            module = __import__(test_name, fromlist=[''])
            suite.addTests(loader.loadTestsFromModule(module))
            print(f"[OK] Loaded {test_name}")
        except ImportError as e:
            print(f"[SKIP] Skipped {test_name}: {e}")
    
    # Remove unit directory from path
    sys.path.pop(0)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    print("Running basic tests (no external dependencies)...")
    sys.exit(run_basic_tests())