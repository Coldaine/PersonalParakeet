#!/usr/bin/env python3
"""
Quick test of application detector
"""

from personalparakeet.core.application_detector import EnhancedApplicationDetector

detector = EnhancedApplicationDetector()
app_info = detector.detect_current_application()

if app_info:
    print(f"Detected app: {app_info.name}")
    print(f"Process name: {app_info.process_name}")
    print(f"Window title: {app_info.window_title}")
    print(f"App type: {app_info.app_type}")
    print(f"Window class: {app_info.window_class}")
    print(f"Extra info: {app_info.extra_info}")
    
    # Get profile
    profile = detector.get_application_profile(app_info)
    print(f"\nProfile: {profile.name}")
    print(f"Preferred strategies: {profile.preferred_strategies}")
else:
    print("No application detected")
    
print(f"\nDetector status: {detector.get_detector_status()}")