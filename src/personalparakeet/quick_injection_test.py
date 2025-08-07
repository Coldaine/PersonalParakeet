#!/usr/bin/env python3
"""
Quick injection test without user input
"""

import sys
import time

from personalparakeet.core.injection_manager import InjectionManager


def test_injection():
    """Test the text injection manager"""
    print("=== PersonalParakeet v3 Quick Injection Test ===")

    # Initialize injection manager
    print("Initializing injection manager...")
    manager = InjectionManager()

    # Get status
    status = manager.get_status()
    print(f"Available strategies: {status['available_strategies']}")

    # Test text injection after short delay
    print("Injecting test text in 3 seconds...")
    time.sleep(3)

    test_text = "Hello from PersonalParakeet v3! This is a test."
    print(f"Injecting: '{test_text}'")
    success = manager.inject_text(test_text)

    if success:
        print("✓ Injection completed successfully")
        return True
    else:
        print("✗ Injection failed")
        return False


if __name__ == "__main__":
    try:
        success = test_injection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)
