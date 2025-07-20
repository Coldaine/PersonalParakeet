#!/usr/bin/env python3
"""Convenience script to run tests from project root"""

import sys
import os
import subprocess

def main():
    """Run tests with appropriate arguments"""
    # Get the path to the tests directory
    tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
    
    # Build command
    if len(sys.argv) > 1 and sys.argv[1] == 'basic':
        # Run basic tests
        script = os.path.join(tests_dir, 'run_basic_tests.py')
        print("Running basic tests (no external dependencies)...")
    else:
        # Run all tests or specific module
        script = os.path.join(tests_dir, 'run_all_tests.py')
        if len(sys.argv) > 1:
            print(f"Running tests for module: {sys.argv[1]}")
        else:
            print("Running all tests...")
    
    # Execute the test runner
    cmd = [sys.executable, script] + sys.argv[1:]
    return subprocess.call(cmd)

if __name__ == '__main__':
    sys.exit(main())