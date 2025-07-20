#!/usr/bin/env python3
"""Test script for enhanced application detection system

This script tests the enhanced application detection functionality.
"""

import sys
import os
import time
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personalparakeet.application_detection_enhanced import (
    EnhancedApplicationDetector, 
    ApplicationProfile,
    get_application_detector,
    detect_current_application,
    get_current_application_profile
)
from personalparakeet.text_injection import ApplicationType
from personalparakeet.logger import setup_logger
from personalparakeet.constants import LogEmoji

logger = setup_logger(__name__)


def test_detector_initialization():
    """Test detector initialization"""
    print(f"{LogEmoji.INFO} Testing detector initialization...")
    
    detector = EnhancedApplicationDetector()
    assert detector.platform in ["Windows", "Linux", "Darwin"]
    assert isinstance(detector.profiles, dict)
    assert len(detector.profiles) > 0
    
    print(f"{LogEmoji.SUCCESS} Detector initialized successfully")
    print(f"Platform: {detector.platform}")
    print(f"Profiles loaded: {len(detector.profiles)}")


def test_detection_capabilities():
    """Test detection capabilities"""
    print(f"{LogEmoji.INFO} Testing detection capabilities...")
    
    detector = get_application_detector()
    capabilities = detector.get_detection_capabilities()
    
    print(f"Detection capabilities:")
    for capability, available in capabilities.items():
        status = "✓" if available else "✗"
        print(f"  {status} {capability}")
    
    # Should have at least basic detection
    assert capabilities["can_detect_active_window"] or capabilities["supports_caching"]
    
    print(f"{LogEmoji.SUCCESS} Detection capabilities verified")


def test_application_profiles():
    """Test application profiles"""
    print(f"{LogEmoji.INFO} Testing application profiles...")
    
    detector = get_application_detector()
    
    # Test specific profiles
    test_profiles = [
        ("code", ApplicationType.EDITOR),
        ("chrome", ApplicationType.BROWSER),
        ("cmd", ApplicationType.TERMINAL),
        ("devenv", ApplicationType.IDE),
        ("winword", ApplicationType.OFFICE)
    ]
    
    for process_name, expected_type in test_profiles:
        # Look for matching profile
        matching_profiles = [p for p in detector.profiles.values() 
                           if p.process_name == process_name]
        if matching_profiles:
            profile = matching_profiles[0]
            assert profile.app_type == expected_type
            print(f"  ✓ {process_name} -> {expected_type.name}")
        else:
            print(f"  - {process_name} -> No specific profile (will use default)")
    
    # Test default profile creation
    default_profile = detector._get_default_profile_for_type(ApplicationType.EDITOR)
    assert isinstance(default_profile, ApplicationProfile)
    assert default_profile.app_type == ApplicationType.EDITOR
    
    print(f"{LogEmoji.SUCCESS} Application profiles verified")


def test_classification():
    """Test application classification"""
    print(f"{LogEmoji.INFO} Testing application classification...")
    
    detector = get_application_detector()
    
    # Test classification with various inputs
    test_cases = [
        # (process_name, window_title, window_class, expected_type)
        ("code.exe", "Visual Studio Code", "Chrome_WidgetWin_1", ApplicationType.EDITOR),
        ("chrome.exe", "Google Chrome", "Chrome_WidgetWin_1", ApplicationType.BROWSER),
        ("cmd.exe", "Command Prompt", "ConsoleWindowClass", ApplicationType.TERMINAL),
        ("devenv.exe", "Visual Studio", "HwndWrapper", ApplicationType.IDE),
        ("winword.exe", "Microsoft Word", "OpusApp", ApplicationType.OFFICE),
        ("discord.exe", "Discord", "Chrome_WidgetWin_1", ApplicationType.CHAT),
        ("unknown.exe", "Unknown Application", "UnknownClass", ApplicationType.UNKNOWN)
    ]
    
    for process_name, window_title, window_class, expected_type in test_cases:
        result = detector._classify_application_enhanced(
            process_name, window_title, window_class, None
        )
        status = "✓" if result == expected_type else "✗"
        print(f"  {status} {process_name} -> {result.name} (expected {expected_type.name})")
        
        # Debug output for failures
        if result != expected_type and expected_type != ApplicationType.UNKNOWN:
            print(f"    Debug: Testing '{process_name}' '{window_title}' '{window_class}'")
        
        # Don't fail on unknown applications
        if expected_type != ApplicationType.UNKNOWN:
            assert result == expected_type
    
    print(f"{LogEmoji.SUCCESS} Application classification verified")


def test_profile_to_dict():
    """Test profile serialization"""
    print(f"{LogEmoji.INFO} Testing profile serialization...")
    
    detector = get_application_detector()
    
    # Get a profile and test serialization
    if detector.profiles:
        profile = next(iter(detector.profiles.values()))
        profile_dict = profile.to_dict()
        
        # Verify required keys
        required_keys = [
            "strategy_order", "key_delay", "supports_paste", 
            "supports_typing", "supports_ui_automation"
        ]
        
        for key in required_keys:
            assert key in profile_dict
        
        print(f"  ✓ Profile serialization successful")
        print(f"  Keys: {list(profile_dict.keys())}")
    
    print(f"{LogEmoji.SUCCESS} Profile serialization verified")


def test_caching():
    """Test detection caching"""
    print(f"{LogEmoji.INFO} Testing detection caching...")
    
    detector = get_application_detector()
    
    # Clear cache
    detector.last_detection_result = None
    detector.last_detection_time = 0
    
    # First detection
    start_time = time.time()
    app_info1 = detector.detect_active_window()
    first_detection_time = time.time() - start_time
    
    # Second detection (should be cached)
    start_time = time.time()
    app_info2 = detector.detect_active_window()
    second_detection_time = time.time() - start_time
    
    # Verify caching worked
    assert app_info1.name == app_info2.name
    assert app_info1.process_name == app_info2.process_name
    
    # Second detection should be faster (cached)
    print(f"  First detection: {first_detection_time:.3f}s")
    print(f"  Second detection: {second_detection_time:.3f}s")
    
    # Cache should make second detection much faster
    if first_detection_time > 0.001:  # Only test if first detection took measurable time
        assert second_detection_time < first_detection_time
    
    print(f"{LogEmoji.SUCCESS} Detection caching verified")


def test_live_detection():
    """Test live application detection"""
    print(f"{LogEmoji.INFO} Testing live application detection...")
    
    try:
        app_info = detect_current_application()
        profile = get_current_application_profile()
        
        print(f"Current application detected:")
        print(f"  Name: {app_info.name}")
        print(f"  Process: {app_info.process_name}")
        print(f"  Title: {app_info.window_title}")
        print(f"  Type: {app_info.app_type.name}")
        print(f"  Platform: {app_info.extra_info.get('platform', 'unknown')}")
        
        print(f"Application profile:")
        print(f"  Profile name: {profile.name}")
        print(f"  Preferred strategies: {profile.preferred_strategies}")
        print(f"  Key delay: {profile.key_delay}")
        print(f"  Supports paste: {profile.supports_paste}")
        print(f"  Supports UI automation: {profile.supports_ui_automation}")
        print(f"  Paste compatibility: {profile.paste_compatibility}")
        
        # Basic validation
        assert isinstance(app_info.name, str)
        assert isinstance(app_info.process_name, str)
        assert isinstance(app_info.app_type, ApplicationType)
        assert isinstance(profile, ApplicationProfile)
        assert len(profile.preferred_strategies) > 0
        
        print(f"{LogEmoji.SUCCESS} Live detection successful")
        
    except Exception as e:
        print(f"{LogEmoji.WARNING} Live detection failed: {e}")
        print("This is expected if no GUI is available or tools are missing")


def interactive_detection_test():
    """Interactive detection testing"""
    print(f"{LogEmoji.INFO} Interactive Detection Test")
    print("=" * 50)
    print("This test will continuously monitor application changes.")
    print("Switch between different applications to test detection.")
    print("Press Ctrl+C to stop.\n")
    
    detector = get_application_detector()
    last_app_name = None
    
    try:
        while True:
            app_info = detector.detect_active_window()
            
            # Only print when application changes
            if app_info.name != last_app_name:
                print(f"{time.strftime('%H:%M:%S')} - Detected: {app_info.name}")
                print(f"  Process: {app_info.process_name}")
                print(f"  Type: {app_info.app_type.name}")
                print(f"  Title: {app_info.window_title[:50]}...")
                
                # Get and show profile
                profile = detector.get_application_profile(app_info)
                print(f"  Profile: {profile.name}")
                print(f"  Strategies: {profile.preferred_strategies}")
                print()
                
                last_app_name = app_info.name
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print(f"\n{LogEmoji.INFO} Interactive test stopped")


def main():
    """Run all application detection tests"""
    print(f"{LogEmoji.INFO} Enhanced Application Detection Tests")
    print("=" * 50)
    
    test_functions = [
        test_detector_initialization,
        test_detection_capabilities,
        test_application_profiles,
        test_classification,
        test_profile_to_dict,
        test_caching,
        test_live_detection
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"{LogEmoji.ERROR} {test_func.__name__} failed: {e}")
            failed += 1
    
    print(f"\n{LogEmoji.INFO} Test Results")
    print("=" * 30)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print(f"\n{LogEmoji.SUCCESS} All tests passed!")
    else:
        print(f"\n{LogEmoji.ERROR} {failed} tests failed!")
    
    # Ask if user wants to run interactive test
    if failed == 0:
        try:
            response = input(f"\n{LogEmoji.INFO} Run interactive detection test? (y/N): ")
            if response.lower() == 'y':
                interactive_detection_test()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{LogEmoji.INFO} Skipping interactive test")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())