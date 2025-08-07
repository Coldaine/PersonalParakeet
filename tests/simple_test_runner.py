#!/usr/bin/env python3
"""
Simple Test Runner for PersonalParakeet
A lightweight alternative to the full dashboard
"""

import subprocess
import sys
from pathlib import Path


def run_test(test_name, test_path):
    """Run a single test and display output"""
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"Path: {test_path}")
    print("=" * 60)

    # Check if file exists
    if not Path(test_path).exists():
        print(f"❌ Test file not found: {test_path}")
        return False

    try:
        # Run the test
        result = subprocess.run(
            [sys.executable, test_path],
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
        )

        # Display output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        # Check result
        if result.returncode == 0:
            print("\n✅ Test completed successfully")
            return True
        else:
            print(f"\n❌ Test failed with exit code {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("\n⚠️ Test timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"\n❌ Error running test: {e}")
        return False


def main():
    """Run all tests"""
    print("PersonalParakeet Simple Test Runner")
    print("==================================")

    # Get project root
    root_dir = Path(__file__).parent.parent

    # Define tests
    tests = [
        (
            "Live Audio Monitor",
            root_dir / "src/personalparakeet/tests/utilities/test_live_audio.py",
        ),
        (
            "Full Pipeline Test",
            root_dir / "src/personalparakeet/tests/utilities/test_full_pipeline.py",
        ),
        ("Microphone Test", root_dir / "src/personalparakeet/tests/utilities/test_microphone.py"),
        ("Window Detection", root_dir / "src/personalparakeet/tests/utilities/test_detector.py"),
        ("Text Injection", root_dir / "src/personalparakeet/tests/utilities/test_injection.py"),
    ]

    # Display menu
    print("\nAvailable tests:")
    for i, (name, _) in enumerate(tests, 1):
        print(f"{i}. {name}")
    print("0. Run all tests")
    print("q. Quit")

    while True:
        choice = input("\nSelect test to run (0-5, q to quit): ").strip().lower()

        if choice == "q":
            print("Goodbye!")
            break

        try:
            choice_num = int(choice)

            if choice_num == 0:
                # Run all tests
                print("\nRunning all tests...")
                results = []
                for name, path in tests:
                    results.append((name, run_test(name, path)))

                # Summary
                print(f"\n{'='*60}")
                print("Test Summary:")
                print("=" * 60)
                for name, passed in results:
                    status = "✅ PASSED" if passed else "❌ FAILED"
                    print(f"{name}: {status}")

            elif 1 <= choice_num <= len(tests):
                # Run single test
                name, path = tests[choice_num - 1]
                run_test(name, path)
            else:
                print("Invalid choice. Please select 0-5 or 'q'")

        except ValueError:
            print("Invalid input. Please enter a number or 'q'")
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break


if __name__ == "__main__":
    # Run from poetry environment if available
    if Path("pyproject.toml").exists():
        # We're likely in the project root, use poetry
        try:
            subprocess.run(["poetry", "run", "python", __file__])
        except Exception:
            # Fallback to direct execution
            main()
    else:
        main()
