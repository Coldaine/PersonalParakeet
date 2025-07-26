#!/usr/bin/env python3
"""Run all tests for the PersonalParakeet project"""

import unittest
import sys
import os

# Add parent directory to path so we can import personalparakeet
# Now we need to go up two levels since we're in tests/utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def run_all_tests():
    """Discover and run all tests in the tests directory"""
    # Create test loader
    loader = unittest.TestLoader()
    
    # Get the tests directory (parent of utils)
    test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Create combined test suite
    suite = unittest.TestSuite()
    
    # Discover tests in each subdirectory
    for subdir in ['unit', 'integration']:
        subdir_path = os.path.join(test_dir, subdir)
        if os.path.exists(subdir_path):
            suite.addTests(loader.discover(subdir_path, pattern='test_*.py'))
    
    # Create test runner with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Run tests
    result = runner.run(suite)
    
    # Return exit code based on success
    return 0 if result.wasSuccessful() else 1


def run_specific_test_module(module_name):
    """Run tests from a specific module"""
    loader = unittest.TestLoader()
    
    # Get the tests directory
    test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Try to find the module in subdirectories
    module_found = False
    for subdir in ['unit', 'integration']:
        test_path = os.path.join(test_dir, subdir, f'test_{module_name}.py')
        if os.path.exists(test_path):
            # Add subdir to path temporarily
            sys.path.insert(0, os.path.join(test_dir, subdir))
            try:
                # Import the test module
                test_module = __import__(f'test_{module_name}', fromlist=[''])
                suite = loader.loadTestsFromModule(test_module)
                
                # Run tests
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(suite)
                
                # Remove subdir from path
                sys.path.pop(0)
                
                return 0 if result.wasSuccessful() else 1
                
            except ImportError as e:
                sys.path.pop(0)
                print(f"Error importing test module: {e}")
                continue
            
            module_found = True
            break
    
    if not module_found:
        print(f"Error: Could not find test module 'test_{module_name}.py'")
        print("\nAvailable test modules:")
        for subdir in ['unit', 'integration']:
            subdir_path = os.path.join(test_dir, subdir)
            if os.path.exists(subdir_path):
                print(f"\n{subdir.capitalize()} tests:")
                for file in os.listdir(subdir_path):
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