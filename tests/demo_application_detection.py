#!/usr/bin/env python3
"""Demo script for enhanced application detection system

This script demonstrates the enhanced application detection functionality
and how it integrates with the text injection system.
"""

import sys
import os
import time
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personalparakeet.application_detection_enhanced import (
    get_application_detector,
    detect_current_application,
    get_current_application_profile
)
from personalparakeet.text_injection_enhanced import EnhancedTextInjectionManager
from personalparakeet.config import InjectionConfig
from personalparakeet.logger import setup_logger
from personalparakeet.constants import LogEmoji

logger = setup_logger(__name__)


def demo_basic_detection():
    """Demo basic application detection"""
    print(f"{LogEmoji.INFO} Basic Application Detection Demo")
    print("=" * 50)
    
    # Get current application
    app_info = detect_current_application()
    
    print(f"Current Application:")
    print(f"  Name: {app_info.name}")
    print(f"  Process: {app_info.process_name}")
    print(f"  Type: {app_info.app_type.name}")
    print(f"  Title: {app_info.window_title}")
    
    if app_info.extra_info:
        print(f"  Platform: {app_info.extra_info.get('platform', 'unknown')}")
        if 'detection_method' in app_info.extra_info:
            print(f"  Detection Method: {app_info.extra_info['detection_method']}")
    
    print()


def demo_application_profiles():
    """Demo application profiles"""
    print(f"{LogEmoji.INFO} Application Profiles Demo")
    print("=" * 50)
    
    detector = get_application_detector()
    
    # Show available profiles
    print(f"Available Application Profiles ({len(detector.profiles)}):")
    for profile_key, profile in detector.profiles.items():
        print(f"  • {profile.name} ({profile.process_name})")
        print(f"    Type: {profile.app_type.name}")
        print(f"    Strategies: {profile.preferred_strategies}")
        print(f"    Key Delay: {profile.key_delay}s")
        print()
    
    # Get profile for current application
    app_info = detect_current_application()
    profile = detector.get_application_profile(app_info)
    
    print(f"Current Application Profile:")
    print(f"  Profile: {profile.name}")
    print(f"  Preferred Strategies: {profile.preferred_strategies}")
    print(f"  Key Delay: {profile.key_delay}s")
    print(f"  Focus Delay: {profile.focus_delay}s")
    print(f"  Supports Paste: {profile.supports_paste}")
    print(f"  Supports UI Automation: {profile.supports_ui_automation}")
    print(f"  Paste Compatibility: {profile.paste_compatibility}")
    print(f"  Unicode Support: {profile.unicode_support}")
    print()


def demo_integration_with_injection():
    """Demo integration with text injection system"""
    print(f"{LogEmoji.INFO} Integration with Text Injection Demo")
    print("=" * 50)
    
    # Create injection manager
    from personalparakeet.config import InjectionConfig
    config = InjectionConfig()
    injection_manager = EnhancedTextInjectionManager(config)
    
    # Get current application
    app_info = detect_current_application()
    
    print(f"Current Application: {app_info.name} ({app_info.app_type.name})")
    
    # Show available strategies
    available_strategies = injection_manager.get_available_strategies()
    print(f"Available Strategies: {available_strategies}")
    
    # Show optimized strategy order
    strategy_order = injection_manager._get_optimized_strategy_order(app_info)
    print(f"Optimized Strategy Order: {strategy_order}")
    
    # Show performance stats
    performance_stats = injection_manager.get_performance_stats()
    if performance_stats:
        print(f"Performance Statistics:")
        for strategy, stats in performance_stats.items():
            print(f"  {strategy}: {stats['success_rate']:.1%} success, {stats['avg_time']:.3f}s avg")
    else:
        print("No performance statistics available yet")
    
    print()


def demo_detection_capabilities():
    """Demo detection capabilities for current platform"""
    print(f"{LogEmoji.INFO} Detection Capabilities Demo")
    print("=" * 50)
    
    detector = get_application_detector()
    capabilities = detector.get_detection_capabilities()
    
    print(f"Platform: {detector.platform}")
    print(f"Detection Capabilities:")
    
    for capability, available in capabilities.items():
        status = "✓" if available else "✗"
        print(f"  {status} {capability}")
    
    print()


def demo_classification():
    """Demo application classification"""
    print(f"{LogEmoji.INFO} Application Classification Demo")
    print("=" * 50)
    
    detector = get_application_detector()
    
    # Test classification with common applications
    test_apps = [
        ("code.exe", "Visual Studio Code", "Chrome_WidgetWin_1"),
        ("chrome.exe", "Google Chrome", "Chrome_WidgetWin_1"),
        ("notepad.exe", "Notepad", "Notepad"),
        ("cmd.exe", "Command Prompt", "ConsoleWindowClass"),
        ("discord.exe", "Discord", "Chrome_WidgetWin_1"),
        ("winword.exe", "Microsoft Word", "OpusApp"),
        ("firefox.exe", "Mozilla Firefox", "MozillaWindowClass"),
        ("powershell.exe", "PowerShell", "ConsoleWindowClass"),
        ("devenv.exe", "Visual Studio", "HwndWrapper"),
        ("slack.exe", "Slack", "Chrome_WidgetWin_1")
    ]
    
    print(f"Classification Examples:")
    for process, title, window_class in test_apps:
        app_type = detector._classify_application_enhanced(process, title, window_class, None)
        print(f"  {process:15} → {app_type.name}")
    
    print()


def interactive_demo():
    """Interactive demo showing live detection"""
    print(f"{LogEmoji.INFO} Interactive Live Detection Demo")
    print("=" * 50)
    print("This demo shows live application detection.")
    print("Switch between different applications to see detection in action.")
    print("Press Ctrl+C to stop.")
    print()
    
    detector = get_application_detector()
    injection_manager = EnhancedTextInjectionManager(InjectionConfig())
    
    last_app = None
    
    try:
        while True:
            app_info = detector.detect_active_window()
            
            if app_info.name != last_app:
                print(f"{time.strftime('%H:%M:%S')} - Active: {app_info.name}")
                print(f"  Process: {app_info.process_name}")
                print(f"  Type: {app_info.app_type.name}")
                print(f"  Title: {app_info.window_title[:40]}...")
                
                # Show optimized strategies
                strategy_order = injection_manager._get_optimized_strategy_order(app_info)
                print(f"  Strategies: {strategy_order}")
                
                # Show profile info
                profile = detector.get_application_profile(app_info)
                print(f"  Profile: {profile.name}")
                print(f"  Key Delay: {profile.key_delay}s")
                print()
                
                last_app = app_info.name
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print(f"\n{LogEmoji.INFO} Live demo stopped")


def main():
    """Run application detection demo"""
    print(f"{LogEmoji.INFO} Enhanced Application Detection Demo")
    print("=" * 60)
    
    demos = [
        ("Basic Detection", demo_basic_detection),
        ("Application Profiles", demo_application_profiles),
        ("Integration with Injection", demo_integration_with_injection),
        ("Detection Capabilities", demo_detection_capabilities),
        ("Classification Examples", demo_classification)
    ]
    
    for demo_name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"{LogEmoji.ERROR} {demo_name} failed: {e}")
    
    # Ask about interactive demo
    try:
        response = input(f"{LogEmoji.INFO} Run interactive live detection demo? (y/N): ")
        if response.lower() == 'y':
            interactive_demo()
    except (KeyboardInterrupt, EOFError):
        print(f"\n{LogEmoji.INFO} Demo completed")
    
    print(f"\n{LogEmoji.SUCCESS} Application detection demo completed!")


if __name__ == "__main__":
    main()