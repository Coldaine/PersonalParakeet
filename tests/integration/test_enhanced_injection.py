#!/usr/bin/env python3
"""Test script for enhanced injection system

This script tests the enhanced injection system and provides benchmarks
comparing the original and improved implementations.
"""

import time
import sys
import os
from typing import Dict, List

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from personalparakeet.text_injection_enhanced import EnhancedTextInjectionManager
from personalparakeet.dictation_enhanced import EnhancedDictationSystem
from personalparakeet.config import InjectionConfig
from personalparakeet.logger import setup_logger
from personalparakeet.constants import LogEmoji

logger = setup_logger(__name__)


def test_enhanced_injection_manager():
    """Test the enhanced injection manager"""
    print(f"{LogEmoji.INFO} Testing Enhanced Injection Manager")
    print("=" * 50)
    
    # Create manager with custom config
    config = InjectionConfig(
        default_key_delay=0.01,
        focus_acquisition_delay=0.05,
        clipboard_paste_delay=0.1
    )
    
    manager = EnhancedTextInjectionManager(config)
    
    # Test 1: Check available strategies
    print(f"\n{LogEmoji.INFO} Test 1: Available Strategies")
    available = manager.get_available_strategies()
    print(f"Available strategies: {available}")
    
    # Test 2: Basic injection test
    print(f"\n{LogEmoji.INFO} Test 2: Basic Injection")
    print("Focus on a text field and press Enter to test injection...")
    input()
    
    test_text = "Hello from Enhanced Injection Manager!"
    result = manager.inject_text(test_text)
    
    print(f"Result: {result.success}")
    print(f"Strategy used: {result.strategy_used}")
    print(f"Time taken: {result.time_taken:.3f}s")
    if result.error_message:
        print(f"Error: {result.error_message}")
    
    # Test 3: Performance statistics
    print(f"\n{LogEmoji.INFO} Test 3: Performance Statistics")
    stats = manager.get_performance_stats()
    for strategy, perf in stats.items():
        print(f"{strategy}:")
        print(f"  Success rate: {perf['success_rate']:.1%}")
        print(f"  Average time: {perf['avg_time']:.3f}s")
        print(f"  Total attempts: {perf['total_attempts']}")
    
    return manager


def test_multiple_injections(manager: EnhancedTextInjectionManager, count: int = 10):
    """Test multiple injections to evaluate performance"""
    print(f"\n{LogEmoji.INFO} Testing Multiple Injections ({count} iterations)")
    print("Focus on a text field and press Enter to start...")
    input()
    
    results = []
    
    for i in range(count):
        test_text = f"Test injection {i+1}"
        start_time = time.time()
        
        result = manager.inject_text(test_text)
        results.append(result)
        
        # Small delay between injections
        time.sleep(0.1)
    
    # Analyze results
    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]
    
    print(f"\nResults:")
    print(f"  Total: {len(results)}")
    print(f"  Successful: {len(successful)} ({len(successful)/len(results)*100:.1f}%)")
    print(f"  Failed: {len(failed)} ({len(failed)/len(results)*100:.1f}%)")
    
    if successful:
        avg_time = sum(r.time_taken for r in successful) / len(successful)
        print(f"  Average time: {avg_time:.3f}s")
        
        # Strategy usage
        strategy_counts = {}
        for r in successful:
            strategy_counts[r.strategy_used] = strategy_counts.get(r.strategy_used, 0) + 1
        
        print(f"  Strategy usage:")
        for strategy, count in strategy_counts.items():
            percentage = count / len(successful) * 100
            print(f"    {strategy}: {count} ({percentage:.1f}%)")
    
    return results


def test_enhanced_dictation_system():
    """Test the enhanced dictation system"""
    print(f"\n{LogEmoji.INFO} Testing Enhanced Dictation System")
    print("=" * 50)
    
    # Create system
    system = EnhancedDictationSystem()
    
    # Test injection strategies
    print(f"\n{LogEmoji.INFO} Testing injection strategies...")
    results = system.test_injection_strategies("Enhanced dictation test")
    
    print(f"\nStrategy test results:")
    for strategy, result in results.items():
        status = "✓" if result.success else "✗"
        time_info = f" ({result.time_taken:.3f}s)" if result.success else ""
        print(f"  {status} {strategy}{time_info}")
    
    # Show statistics
    print(f"\n{LogEmoji.INFO} Current statistics:")
    system.print_injection_statistics()
    
    return system


def benchmark_injection_performance():
    """Benchmark injection performance"""
    print(f"\n{LogEmoji.INFO} Benchmarking Injection Performance")
    print("=" * 50)
    
    # Test different text sizes
    test_texts = [
        "Short",
        "Medium length text for testing",
        "This is a longer text that might be typical of dictation output from a voice recognition system.",
        "Very long text that includes multiple sentences and various types of content including numbers like 123 and symbols like @#$%^&*() to test the robustness of the injection system across different character types and text lengths."
    ]
    
    manager = EnhancedTextInjectionManager()
    
    print("Focus on a text field and press Enter to start benchmark...")
    input()
    
    for i, text in enumerate(test_texts):
        print(f"\nTest {i+1}: {len(text)} characters")
        print(f"Text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
        
        # Test each text multiple times
        times = []
        successes = 0
        
        for _ in range(3):
            result = manager.inject_text(text)
            times.append(result.time_taken)
            if result.success:
                successes += 1
            time.sleep(0.2)
        
        avg_time = sum(times) / len(times)
        success_rate = successes / len(times) * 100
        
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Success rate: {success_rate:.1f}%")
        print(f"  Characters per second: {len(text) / avg_time:.1f}")


def test_special_characters():
    """Test injection with special characters"""
    print(f"\n{LogEmoji.INFO} Testing Special Characters")
    print("=" * 50)
    
    special_tests = [
        ("Unicode", "Hello 世界 🌍 Testing"),
        ("Symbols", "Testing @#$%^&*()_+-=[]{}|;:,.<>?"),
        ("Quotes", 'Both "double" and \'single\' quotes'),
        ("Newlines", "Line 1\nLine 2\nLine 3"),
        ("Tabs", "Col1\tCol2\tCol3"),
        ("Mixed", "Mix: 123 + symbols @#$ + unicode 🚀 + quotes \"test\"")
    ]
    
    manager = EnhancedTextInjectionManager()
    
    print("Focus on a text field and press Enter to start special character tests...")
    input()
    
    for test_name, test_text in special_tests:
        print(f"\n{LogEmoji.INFO} Testing {test_name}: '{test_text}'")
        
        result = manager.inject_text(test_text)
        
        status = "✓" if result.success else "✗"
        time_info = f" ({result.time_taken:.3f}s)" if result.success else ""
        error_info = f" - {result.error_message}" if result.error_message else ""
        
        print(f"  {status} {result.strategy_used}{time_info}{error_info}")
        
        time.sleep(1)


def interactive_menu():
    """Interactive menu for testing"""
    while True:
        print(f"\n{LogEmoji.INFO} Enhanced Injection Test Menu")
        print("=" * 40)
        print("1. Test Enhanced Injection Manager")
        print("2. Test Multiple Injections")
        print("3. Test Enhanced Dictation System")
        print("4. Benchmark Performance")
        print("5. Test Special Characters")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            test_enhanced_injection_manager()
        elif choice == '2':
            manager = EnhancedTextInjectionManager()
            count = int(input("Enter number of injections to test (default 10): ") or "10")
            test_multiple_injections(manager, count)
        elif choice == '3':
            test_enhanced_dictation_system()
        elif choice == '4':
            benchmark_injection_performance()
        elif choice == '5':
            test_special_characters()
        elif choice == '6':
            print("Goodbye!")
            break
        else:
            print("Invalid option, please try again.")


def main():
    """Main function"""
    print(f"{LogEmoji.INFO} Enhanced Injection System Test Suite")
    print("=" * 50)
    
    # Check platform
    import platform
    if platform.system() != 'Windows':
        print(f"{LogEmoji.WARNING} Note: Enhanced strategies are optimized for Windows")
        print("Basic strategies will be used on other platforms.")
    
    # Run interactive menu
    interactive_menu()


if __name__ == "__main__":
    main()