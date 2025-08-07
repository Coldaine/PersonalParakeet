#!/usr/bin/env python
"""Test runner for PersonalParakeet hardware tests."""

import argparse
import sys
from pathlib import Path

import pytest


def main():
    """Run PersonalParakeet tests with various configurations."""
    parser = argparse.ArgumentParser(description="PersonalParakeet Test Runner")

    # Test selection
    parser.add_argument("tests", nargs="*", help="Specific test files or directories to run")

    # Test categories
    parser.add_argument("--hardware", action="store_true", help="Run hardware tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument(
        "--interactive", action="store_true", help="Run interactive tests (requires human input)"
    )
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmarks")
    parser.add_argument(
        "--quick", action="store_true", help="Run quick tests only (exclude slow/gpu_intensive)"
    )

    # Hardware options
    parser.add_argument("--no-gpu", action="store_true", help="Skip GPU-intensive tests")

    # Output options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--report", action="store_true", help="Generate detailed test report")

    args = parser.parse_args()

    # Build pytest arguments
    pytest_args = []

    # Add test paths
    if args.tests:
        pytest_args.extend(args.tests)
    else:
        pytest_args.append("tests/")

    # Add markers
    markers = []
    if args.hardware:
        markers.append("hardware")
    if args.integration:
        markers.append("integration")
    if args.interactive:
        markers.append("interactive")
    if args.benchmark:
        markers.append("benchmark")

    if markers:
        pytest_args.extend(["-m", " or ".join(markers)])
    elif args.quick:
        pytest_args.extend(["-m", "not slow and not gpu_intensive"])

    # Skip GPU tests if requested
    if args.no_gpu:
        if "-m" in pytest_args:
            idx = pytest_args.index("-m")
            pytest_args[idx + 1] += " and not gpu_intensive"
        else:
            pytest_args.extend(["-m", "not gpu_intensive"])

    # Verbosity
    if args.verbose:
        pytest_args.append("-vv")

    # Report generation
    if args.report:
        pytest_args.extend(
            ["--tb=short", f"--html=test_reports/report.html", "--self-contained-html"]
        )

    print("PersonalParakeet Test Suite")
    print("=" * 50)
    print(f"Running: pytest {' '.join(pytest_args)}")
    print("=" * 50)

    # Run tests
    exit_code = pytest.main(pytest_args)

    if args.report and exit_code == 0:
        print(f"\nTest report generated: test_reports/report.html")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
