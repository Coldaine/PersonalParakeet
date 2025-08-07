#!/usr/bin/env python3
"""
Simple test to verify text injection functionality
"""

import sys
import time

from personalparakeet.core.injection_manager import InjectionManager


def test_injection():
    """Test the text injection manager"""
    print("=== PersonalParakeet v3 Text Injection Test ===")

    # Initialize injection manager
    print("Initializing injection manager...")
    manager = InjectionManager()

    # Get status
    status = manager.get_status()
    print(f"Available strategies: {status['available_strategies']}")
    print(f"Total injection count: {status['injection_count']}")

    # Give user time to focus on a text editor
    print("\nPlease focus on a text editor (notepad, VS Code, etc.) and then press Enter...")
    input()

    # Test text injection
    test_texts = [
        "Hello from PersonalParakeet v3!",
        "This text was injected using the automated system.",
        "The injection functionality is working correctly.",
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"Injecting text {i}/3: '{text[:30]}...'")
        success = manager.inject_text(text)

        if success:
            print(f"✓ Injection {i} completed successfully")
        else:
            print(f"✗ Injection {i} failed")

        # Wait between injections
        time.sleep(2)

    # Final status
    final_status = manager.get_status()
    print(f"\nFinal injection count: {final_status['injection_count']}")
    print("Test completed!")

    return final_status["injection_count"] > 0


if __name__ == "__main__":
    try:
        success = test_injection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1)
