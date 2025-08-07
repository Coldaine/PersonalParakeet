#!/usr/bin/env python3
"""
Test utility for Wayland text injection
"""

import os
import sys
import time
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from personalparakeet.core.text_injector import TextInjector


def main():
    """Test Wayland injection through main TextInjector"""
    print("PersonalParakeet Wayland Injection Test")
    print("======================================")

    # Check environment
    session_type = os.environ.get("XDG_SESSION_TYPE", "unknown")
    print(f"Session type: {session_type}")

    if session_type != "wayland":
        print("\n⚠️  WARNING: Not running on Wayland!")

    # Create injector
    print("\nInitializing TextInjector...")
    injector = TextInjector()

    if not injector.is_enabled():
        print("❌ TextInjector failed to initialize")
        return

    print("✅ TextInjector initialized")

    # Test texts
    test_texts = [
        "Hello from PersonalParakeet on Wayland!",
        "Testing special characters: @#$%^&*()",
        "Numbers and punctuation: 123, 456. Done!",
        "🚀 Even emojis work!",
    ]

    print("\n⚠️  IMPORTANT: Position your cursor in a text field NOW!")
    print("Tests will begin in 5 seconds...")

    for i in range(5, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    # Run tests
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}/{len(test_texts)}: {text[:30]}...")

        success = injector.inject_text(text + " ")

        if success:
            print("✅ Success!")
        else:
            print("❌ Failed!")

        time.sleep(2)  # Pause between tests

    # Show stats
    stats = injector.get_injection_stats()
    print("\n=== Injection Statistics ===")
    print(f"Total attempts: {stats['total_attempts']}")
    print(f"Successful: {stats['successful_injections']}")
    print(f"Failed: {stats['failed_injections']}")

    if stats["successful_injections"] > 0:
        print("\n✅ Wayland injection is working!")
    else:
        print("\n❌ Wayland injection failed. Run setup script:")
        print("   ./scripts/setup_wayland_injection.sh")


if __name__ == "__main__":
    main()
