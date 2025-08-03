#!/usr/bin/env python3
"""
Comprehensive tests for enhanced injection system
Tests all strategies, performance tracking, and application-specific optimizations
"""

import time
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from personalparakeet.core.injection_manager_enhanced import EnhancedInjectionManager
from personalparakeet.core.application_detector import ApplicationInfo, ApplicationType

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_basic_injection():
    """Test basic text injection functionality"""
    print("\n=== Testing Basic Injection ===")
    
    manager = EnhancedInjectionManager()
    
    # Print available strategies
    status = manager.get_status()
    print(f"Available strategies: {status['available_strategies']}")
    
    # Test simple text
    test_texts = [
        "Hello, world!",
        "Testing enhanced injection.",
        "Unicode test: こんにちは 🎉",
        "Multi-line\ntext test"
    ]
    
    for text in test_texts:
        print(f"\nInjecting: '{text}'")
        success = manager.inject_text(text)
        print(f"Result: {'✓ Success' if success else '✗ Failed'}")
        time.sleep(0.5)


def test_strategy_performance():
    """Test strategy performance tracking"""
    print("\n=== Testing Strategy Performance ===")
    
    manager = EnhancedInjectionManager()
    
    # Inject multiple times to build statistics
    test_text = "Performance test"
    
    print("Injecting text 5 times...")
    for i in range(5):
        print(f"  Injection {i+1}...", end="")
        success = manager.inject_text(test_text)
        print(f" {'✓' if success else '✗'}")
        time.sleep(0.3)
    
    # Get performance stats
    stats = manager.get_performance_stats()
    
    print(f"\nPerformance Statistics:")
    print(f"  Total injections: {stats['total_injections']}")
    print(f"  Successful: {stats['successful_injections']}")
    print(f"  Failed: {stats['failed_injections']}")
    print(f"  Success rate: {stats['success_rate_percent']}%")
    print(f"  Average time: {stats['average_injection_time_ms']}ms")
    
    # Strategy-specific stats
    if 'strategy_performance' in stats:
        print("\nStrategy Performance:")
        for strategy, perf in stats['strategy_performance'].items():
            print(f"  {strategy}:")
            print(f"    Success rate: {perf.get('success_rate', 0)*100:.1f}%")
            print(f"    Average time: {perf.get('average_time', 0)*1000:.1f}ms")
            print(f"    Consecutive failures: {perf.get('consecutive_failures', 0)}")


def test_application_specific_injection():
    """Test application-specific injection optimization"""
    print("\n=== Testing Application-Specific Injection ===")
    
    manager = EnhancedInjectionManager()
    
    # Detect current application
    app_info = manager.get_current_application()
    if app_info:
        print(f"Current application: {app_info.name} ({app_info.app_type.name})")
        print(f"Window title: {app_info.window_title}")
    else:
        print("Could not detect current application")
    
    # Test injection with app context
    test_text = "Application-aware injection test"
    print(f"\nInjecting with app context: '{test_text}'")
    success = manager.inject_text(test_text, app_info)
    print(f"Result: {'✓ Success' if success else '✗ Failed'}")


def test_fallback_display():
    """Test fallback display callback"""
    print("\n=== Testing Fallback Display ===")
    
    manager = EnhancedInjectionManager()
    
    # Set up fallback display
    fallback_texts = []
    def fallback_callback(text):
        fallback_texts.append(text)
        print(f"  [FALLBACK] Would display: '{text}'")
    
    manager.set_fallback_display(fallback_callback)
    
    # Force all strategies to fail by injecting when no window is focused
    print("Testing fallback when injection fails...")
    print("(Switch to desktop or minimize all windows)")
    time.sleep(2)
    
    test_text = "This should trigger fallback"
    manager.inject_text(test_text)
    
    if fallback_texts:
        print(f"✓ Fallback display triggered for: {fallback_texts}")
    else:
        print("✗ Fallback display not triggered (injection may have succeeded)")


def test_strategy_forcing():
    """Test forcing specific strategy order"""
    print("\n=== Testing Strategy Order Forcing ===")
    
    manager = EnhancedInjectionManager()
    
    # Force clipboard-first order
    print("Forcing clipboard-first strategy order...")
    manager.force_strategy_order(['clipboard', 'keyboard', 'ui_automation', 'win32_sendinput'])
    
    test_text = "Testing forced strategy order"
    success = manager.inject_text(test_text)
    print(f"Result: {'✓ Success' if success else '✗ Failed'}")
    
    # Check which strategy was used
    stats = manager.get_performance_stats()
    if 'strategy_usage' in stats:
        print("\nStrategy usage after forcing:")
        for strategy, usage in stats['strategy_usage'].items():
            if usage['attempts'] > 0:
                print(f"  {strategy}: {usage['attempts']} attempts, {usage['successes']} successes")


def test_async_injection():
    """Test asynchronous injection"""
    print("\n=== Testing Async Injection ===")
    
    manager = EnhancedInjectionManager()
    
    print("Starting async injection...")
    test_text = "Async injection test - this should not block"
    
    # Start async injection
    queued = manager.inject_text_async(test_text)
    print(f"Injection queued: {'✓' if queued else '✗'}")
    
    # Do other work while injection happens
    print("Doing other work...")
    for i in range(3):
        print(f"  Working... {i+1}")
        time.sleep(0.2)
    
    # Wait a bit more to ensure injection completes
    time.sleep(0.5)
    print("Async injection should be complete")


def test_performance_reset():
    """Test resetting performance statistics"""
    print("\n=== Testing Performance Reset ===")
    
    manager = EnhancedInjectionManager()
    
    # Do some injections
    print("Performing initial injections...")
    for i in range(3):
        manager.inject_text(f"Test {i+1}")
        time.sleep(0.2)
    
    # Check stats
    stats = manager.get_performance_stats()
    print(f"Stats before reset: {stats['total_injections']} injections")
    
    # Reset stats
    print("Resetting statistics...")
    manager.reset_performance_stats()
    
    # Check stats again
    stats = manager.get_performance_stats()
    print(f"Stats after reset: {stats['total_injections']} injections")
    
    if stats['total_injections'] == 0:
        print("✓ Performance stats reset successfully")
    else:
        print("✗ Performance stats not reset properly")


def run_all_tests():
    """Run all tests"""
    print("=== PersonalParakeet v3 Enhanced Injection Tests ===")
    print("Note: Some tests require user interaction (switching windows, etc.)")
    
    tests = [
        test_basic_injection,
        test_strategy_performance,
        test_application_specific_injection,
        test_fallback_display,
        test_strategy_forcing,
        test_async_injection,
        test_performance_reset
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"\n✗ Test {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Pause between tests
        if test != tests[-1]:
            print("\nPress Enter to continue to next test...")
            input()
    
    print("\n=== All tests completed ===")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test enhanced injection system")
    parser.add_argument('--test', choices=[
        'basic', 'performance', 'app-specific', 'fallback', 
        'forcing', 'async', 'reset', 'all'
    ], default='all', help='Specific test to run')
    
    args = parser.parse_args()
    
    if args.test == 'all':
        run_all_tests()
    else:
        test_map = {
            'basic': test_basic_injection,
            'performance': test_strategy_performance,
            'app-specific': test_application_specific_injection,
            'fallback': test_fallback_display,
            'forcing': test_strategy_forcing,
            'async': test_async_injection,
            'reset': test_performance_reset
        }
        
        if args.test in test_map:
            test_map[args.test]()
        else:
            print(f"Unknown test: {args.test}")