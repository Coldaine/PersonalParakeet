#!/usr/bin/env python3
"""Run all tests for the PersonalParakeet project"""

import unittest
import sys
import os

# Add parent directory to path so we can import personalparakeet
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_all_tests():
    """Discover and run all tests in the tests directory"""
    # Create test loader
    loader = unittest.TestLoader()
    
    # Discover all tests in the current directory
    test_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(test_dir, pattern='test_*.py')
    
    # Create test runner with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run tests
    result = runner.run(suite)
    
    # Return exit code based on success
    return 0 if result.wasSuccessful() else 1


def run_specific_test_module(module_name):
    """Run tests from a specific module"""
    loader = unittest.TestLoader()
    
    try:
        # Import the test module
        test_module = __import__(f'test_{module_name}', fromlist=[''])
        suite = loader.loadTestsFromModule(test_module)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
        
    except ImportError as e:
        print(f"Error: Could not import test module 'test_{module_name}': {e}")
        print("\nAvailable test modules:")
        test_dir = os.path.dirname(os.path.abspath(__file__))
        for file in os.listdir(test_dir):
            if file.startswith('test_') and file.endswith('.py'):
                print(f"  - {file[5:-3]}")  # Remove 'test_' prefix and '.py' suffix
        return 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test module
        module_name = sys.argv[1]
        print(f"Running tests from test_{module_name}.py...")
        exit_code = run_specific_test_module(module_name)
    else:
        # Run all tests
        print("Running all tests...")
        exit_code = run_all_tests()
        
    sys.exit(exit_code)