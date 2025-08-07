#!/usr/bin/env python3
"""
Test script for Enhanced Application Detection in PersonalParakeet v3

This script tests the application detection functionality and demonstrates
the integration with the injection manager.
"""

import sys
import time
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from personalparakeet.core.application_detector import EnhancedApplicationDetector, ApplicationType
from personalparakeet.core.injection_manager import InjectionManager

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_application_detection():
    """Test basic application detection functionality"""
    print("🔍 Testing Enhanced Application Detection")
    print("=" * 50)

    # Initialize detector
    detector = EnhancedApplicationDetector()

    # Show detector status
    status = detector.get_detector_status()
    print(f"Platform: {status['platform']}")
    print(f"Profiles loaded: {status['profiles_loaded']}")
    print(f"Detection capabilities: {[k for k, v in status.items() if k.startswith('has_') and v]}")
    print()

    # Test detection multiple times to show caching
    print("🎯 Detecting current application (5 attempts):")
    for i in range(5):
        app_info = detector.detect_current_application()
        if app_info:
            print(
                f"  {i+1}. {app_info.name} ({app_info.app_type.name}) - '{app_info.window_title[:50]}...'"
            )

            # Get application profile
            profile = detector.get_application_profile(app_info)
            print(f"     Strategy order: {profile.preferred_strategies}")
            print(
                f"     Performance: key_delay={profile.key_delay}ms, supports_paste={profile.supports_paste}"
            )
        else:
            print(f"  {i+1}. Detection failed")

        time.sleep(0.5)  # Small delay between detections

    print()


def test_injection_manager_integration():
    """Test integration with injection manager"""
    print("🚀 Testing Injection Manager Integration")
    print("=" * 50)

    # Initialize injection manager (includes application detector)
    manager = InjectionManager()

    # Get current status
    status = manager.get_status()
    print(f"Current application: {status['current_application']}")
    print(f"Available strategies: {status['available_strategies']}")
    print()

    # Get performance stats
    perf_stats = manager.get_performance_stats()
    print("Performance Statistics:")
    print(f"  Total injections: {perf_stats['total_injections']}")
    print(f"  Success rate: {perf_stats['success_rate_percent']}%")
    print(f"  App type distribution: {perf_stats['app_type_distribution']}")
    print()

    # Test dry run (just detection without actual injection)
    print("Testing application-aware strategy selection:")
    app_info = manager.get_current_application()
    if app_info:
        profile = manager.get_application_profile(app_info)
        print(f"  Detected: {app_info.name} ({app_info.app_type.name})")
        print(f"  Optimized strategies: {profile.preferred_strategies}")
        print(
            f"  Profile settings: key_delay={profile.key_delay}, focus_delay={profile.focus_delay}"
        )

        # Show how strategy order would be updated
        strategy_order = manager.app_detector.get_optimized_strategy_order(app_info)
        print(f"  Strategy order for this app: {strategy_order}")
    else:
        print("  No application detected")

    print()


def test_application_classification():
    """Test application classification logic"""
    print("🏷️  Testing Application Classification")
    print("=" * 50)

    detector = EnhancedApplicationDetector()

    # Test various application names
    test_cases = [
        ("code.exe", "Visual Studio Code - test.py", ""),
        ("chrome.exe", "Google Chrome - Stack Overflow", ""),
        ("cmd.exe", "Command Prompt", ""),
        ("powershell.exe", "Windows PowerShell", ""),
        ("notepad.exe", "Untitled - Notepad", ""),
        ("firefox.exe", "Mozilla Firefox", ""),
        ("slack.exe", "Slack - PersonalParakeet Team", ""),
        ("unknown_app.exe", "Some Unknown Application", ""),
    ]

    for process_name, window_title, window_class in test_cases:
        app_type = detector._classify_application(process_name, window_title, window_class)
        profile = detector.profiles.get(process_name.lower())

        if not profile:
            # Try type-based profile
            type_key = f"type_{app_type.name.lower()}"
            profile = detector.profiles.get(type_key, detector._get_default_profile())

        print(f"  {process_name:<20} → {app_type.name:<10} → {profile.preferred_strategies}")

    print()


def interactive_detection_test():
    """Interactive test - user switches between applications"""
    print("🔄 Interactive Detection Test")
    print("=" * 50)
    print("Switch between different applications and press Enter to detect.")
    print("Applications to try: VS Code, Chrome, Terminal, Notepad, etc.")
    print("Press 'q' + Enter to quit.")
    print()

    detector = EnhancedApplicationDetector()

    while True:
        user_input = input("Press Enter to detect current app (or 'q' to quit): ").strip()
        if user_input.lower() == "q":
            break

        app_info = detector.detect_current_application()
        if app_info:
            profile = detector.get_application_profile(app_info)
            print(f"  📱 App: {app_info.name}")
            print(f"  📋 Type: {app_info.app_type.name}")
            print(f"  🪟 Window: '{app_info.window_title[:60]}...'")
            print(f"  ⚡ Strategies: {profile.preferred_strategies}")
            print(
                f"  ⏱️  Timing: key_delay={profile.key_delay}ms, focus_delay={profile.focus_delay}ms"
            )
            print()
        else:
            print("  ❌ Could not detect current application")
            print()


def main():
    """Main test function"""
    print("🦜 PersonalParakeet v3 - Enhanced Application Detection Test")
    print("=" * 60)
    print()

    try:
        # Run all tests
        test_application_detection()
        test_injection_manager_integration()
        test_application_classification()

        # Interactive test (optional)
        print("Would you like to run the interactive detection test?")
        response = input(
            "This lets you switch between apps and see real-time detection (y/n): "
        ).strip()
        if response.lower() in ["y", "yes"]:
            interactive_detection_test()

        print("✅ All tests completed successfully!")

    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
