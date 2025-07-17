"""Test the new text injection system

This script tests the platform-aware text injection system
with application detection and multiple injection strategies.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from personalparakeet.text_injection import TextInjectionManager, PlatformDetector
from personalparakeet.application_detection import ApplicationDetector


def test_platform_detection():
    """Test platform detection"""
    print("=" * 60)
    print("PLATFORM DETECTION TEST")
    print("=" * 60)
    
    platform_info = PlatformDetector.detect()
    print(f"Platform: {platform_info.platform.name}")
    print(f"Desktop Environment: {platform_info.desktop_env.name}")
    print(f"Session Type: {platform_info.session_type.name}")
    print(f"Version: {platform_info.version}")
    print(f"Extra Info: {platform_info.extra_info}")
    print()


def test_application_detection():
    """Test application detection"""
    print("=" * 60)
    print("APPLICATION DETECTION TEST")
    print("=" * 60)
    
    detector = ApplicationDetector()
    print("Please click on different applications to test detection...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            app_info = detector.detect_active_window()
            print(f"Active Application: {app_info.name}")
            print(f"Process: {app_info.process_name}")
            print(f"Window Title: {app_info.window_title}")
            print(f"Type: {app_info.app_type.name}")
            print(f"Capabilities: {detector.get_injection_capabilities(app_info)}")
            print("-" * 40)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nApplication detection test stopped")


def test_text_injection():
    """Test text injection"""
    print("\n" + "=" * 60)
    print("TEXT INJECTION TEST")
    print("=" * 60)
    
    manager = TextInjectionManager()
    
    print(f"Platform: {manager.platform_info.platform.name}")
    print(f"Available strategies: {list(manager.strategies.keys())}")
    print()
    
    test_messages = [
        "Hello from PersonalParakeet",
        "Testing text injection system",
        "Platform-aware injection works!"
    ]
    
    print("Starting text injection in 3 seconds...")
    print("Make sure to focus on a text editor or input field!")
    
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    for msg in test_messages:
        print(f"\nInjecting: '{msg}'")
        success = manager.inject_text(msg)
        if success:
            print("[PASS] Injection successful!")
        else:
            print("[FAIL] Injection failed!")
        time.sleep(1)


def test_fallback_display():
    """Test fallback display mechanism"""
    print("\n" + "=" * 60)
    print("FALLBACK DISPLAY TEST")
    print("=" * 60)
    
    def custom_fallback(text):
        print(f"\nWARNING: FALLBACK DISPLAY")
        print(f"Text to copy: {text}")
        print("=" * 40 + "\n")
    
    manager = TextInjectionManager()
    manager.set_fallback_display(custom_fallback)
    
    # Force fallback by clearing all strategies
    manager.strategies.clear()
    
    print("Testing fallback display (all strategies disabled)...")
    manager.inject_text("This should appear in fallback display")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PERSONALPARAKEET TEXT INJECTION SYSTEM TEST")
    print("=" * 60 + "\n")
    
    # Test platform detection
    test_platform_detection()
    
    # Ask user which tests to run
    print("\nAvailable tests:")
    print("1. Application Detection (interactive)")
    print("2. Text Injection")
    print("3. Fallback Display")
    print("4. All tests")
    
    choice = input("\nSelect test (1-4): ")
    
    if choice == "1":
        test_application_detection()
    elif choice == "2":
        test_text_injection()
    elif choice == "3":
        test_fallback_display()
    elif choice == "4":
        test_application_detection()
        test_text_injection()
        test_fallback_display()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()