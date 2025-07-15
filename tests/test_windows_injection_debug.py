#!/usr/bin/env python3
"""Debug and test utility for Windows injection strategies

This utility helps debug and test the Windows injection strategies
with real applications and provides detailed diagnostics.
"""

import time
import sys
import os
import threading
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from personalparakeet.windows_injection_improved import (
    ImprovedWindowsUIAutomationStrategy,
    ImprovedWindowsKeyboardStrategy,
    ImprovedWindowsClipboardStrategy,
    ImprovedWindowsSendInputStrategy
)
from personalparakeet.config import InjectionConfig
from personalparakeet.text_injection import ApplicationInfo, ApplicationType
from personalparakeet.logger import setup_logger

logger = setup_logger(__name__)


class WindowsInjectionDebugger:
    """Debug utility for Windows injection strategies"""
    
    def __init__(self):
        self.config = InjectionConfig()
        self.strategies = {}
        self.test_results = {}
        self._init_strategies()
    
    def _init_strategies(self):
        """Initialize all available strategies"""
        strategy_classes = {
            'ui_automation': ImprovedWindowsUIAutomationStrategy,
            'keyboard': ImprovedWindowsKeyboardStrategy,
            'clipboard': ImprovedWindowsClipboardStrategy,
            'send_input': ImprovedWindowsSendInputStrategy
        }
        
        for name, strategy_class in strategy_classes.items():
            try:
                strategy = strategy_class(self.config)
                self.strategies[name] = strategy
                print(f"✓ {name} strategy initialized")
            except Exception as e:
                print(f"✗ {name} strategy failed to initialize: {e}")
    
    def check_availability(self):
        """Check which strategies are available"""
        print("\n=== Strategy Availability Check ===")
        for name, strategy in self.strategies.items():
            available = strategy.is_available()
            status = "✓ Available" if available else "✗ Not Available"
            print(f"{name}: {status}")
        return {name: strategy.is_available() for name, strategy in self.strategies.items()}
    
    def test_basic_injection(self, test_text: str = "Hello World Test"):
        """Test basic injection with all strategies"""
        print(f"\n=== Basic Injection Test ===")
        print(f"Test text: '{test_text}'")
        print("Click on a text field and press Enter to continue...")
        input()
        
        results = {}
        for name, strategy in self.strategies.items():
            if not strategy.is_available():
                print(f"⏭️  Skipping {name} (not available)")
                results[name] = False
                continue
            
            print(f"\n🧪 Testing {name} strategy...")
            print("You have 3 seconds to focus on the target application...")
            time.sleep(3)
            
            try:
                success = strategy.inject(test_text)
                status = "✓ Success" if success else "✗ Failed"
                print(f"{name}: {status}")
                results[name] = success
            except Exception as e:
                print(f"{name}: ✗ Exception - {e}")
                results[name] = False
            
            # Give time to see the result
            time.sleep(2)
        
        return results
    
    def test_application_specific(self):
        """Test injection with different application types"""
        print("\n=== Application-Specific Testing ===")
        
        app_types = [
            ("Notepad", ApplicationType.EDITOR),
            ("Browser", ApplicationType.BROWSER),
            ("VS Code", ApplicationType.IDE),
            ("Command Prompt", ApplicationType.TERMINAL)
        ]
        
        results = {}
        for app_name, app_type in app_types:
            print(f"\n📱 Testing with {app_name} ({app_type.name})")
            print(f"Open {app_name} and focus on a text input, then press Enter...")
            input()
            
            app_info = ApplicationInfo(
                name=app_name,
                app_type=app_type,
                process_name=f"{app_name.lower().replace(' ', '')}.exe",
                window_title=app_name
            )
            
            app_results = {}
            test_text = f"Test in {app_name}"
            
            for name, strategy in self.strategies.items():
                if not strategy.is_available():
                    continue
                
                print(f"  🧪 Testing {name} with {app_name}...")
                time.sleep(1)
                
                try:
                    success = strategy.inject(test_text, app_info)
                    app_results[name] = success
                    status = "✓" if success else "✗"
                    print(f"    {status} {name}")
                except Exception as e:
                    app_results[name] = False
                    print(f"    ✗ {name} - Exception: {e}")
                
                time.sleep(1)
            
            results[app_name] = app_results
        
        return results
    
    def test_performance(self, iterations: int = 10):
        """Test performance of different strategies"""
        print(f"\n=== Performance Testing ({iterations} iterations) ===")
        print("Focus on a text field and press Enter to start...")
        input()
        
        test_text = "Performance test text"
        results = {}
        
        for name, strategy in self.strategies.items():
            if not strategy.is_available():
                continue
            
            print(f"\n⏱️  Testing {name} performance...")
            times = []
            successes = 0
            
            for i in range(iterations):
                start_time = time.time()
                try:
                    success = strategy.inject(f"{test_text} {i}")
                    if success:
                        successes += 1
                except Exception as e:
                    print(f"    Iteration {i}: Exception - {e}")
                
                end_time = time.time()
                times.append(end_time - start_time)
                time.sleep(0.1)  # Small delay between iterations
            
            if times:
                avg_time = sum(times) / len(times)
                success_rate = successes / iterations * 100
                print(f"    Average time: {avg_time:.3f}s")
                print(f"    Success rate: {success_rate:.1f}%")
                
                results[name] = {
                    'avg_time': avg_time,
                    'success_rate': success_rate,
                    'total_iterations': iterations
                }
        
        return results
    
    def test_special_characters(self):
        """Test injection with special characters"""
        print("\n=== Special Character Testing ===")
        
        special_tests = [
            ("Unicode", "Hello 世界 🌍"),
            ("Symbols", "Test @#$%^&*()_+-=[]{}|;:,.<>?"),
            ("Newlines", "Line 1\nLine 2\nLine 3"),
            ("Tabs", "Col1\tCol2\tCol3"),
            ("Quotes", 'Single "quotes" and \'apostrophes\''),
            ("Numbers", "123456789 3.14159 -42"),
        ]
        
        results = {}
        
        for test_name, test_text in special_tests:
            print(f"\n🔤 Testing {test_name}: '{test_text}'")
            print("Focus on a text field and press Enter...")
            input()
            
            test_results = {}
            for name, strategy in self.strategies.items():
                if not strategy.is_available():
                    continue
                
                print(f"  Testing {name}...")
                time.sleep(1)
                
                try:
                    success = strategy.inject(test_text)
                    test_results[name] = success
                    status = "✓" if success else "✗"
                    print(f"    {status} {name}")
                except Exception as e:
                    test_results[name] = False
                    print(f"    ✗ {name} - Exception: {e}")
                
                time.sleep(1)
            
            results[test_name] = test_results
        
        return results
    
    def generate_report(self, all_results: Dict):
        """Generate a comprehensive test report"""
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST REPORT")
        print("="*60)
        
        # Strategy availability
        if 'availability' in all_results:
            print("\n📊 Strategy Availability:")
            for name, available in all_results['availability'].items():
                status = "✓" if available else "✗"
                print(f"  {status} {name}")
        
        # Basic injection results
        if 'basic' in all_results:
            print("\n📝 Basic Injection Results:")
            for name, success in all_results['basic'].items():
                status = "✓" if success else "✗"
                print(f"  {status} {name}")
        
        # Performance results
        if 'performance' in all_results:
            print("\n⏱️  Performance Results:")
            for name, perf in all_results['performance'].items():
                print(f"  {name}:")
                print(f"    Average time: {perf['avg_time']:.3f}s")
                print(f"    Success rate: {perf['success_rate']:.1f}%")
        
        # Recommendations
        print("\n💡 Recommendations:")
        if 'basic' in all_results:
            best_strategies = [name for name, success in all_results['basic'].items() if success]
            if best_strategies:
                print(f"  Best performing strategies: {', '.join(best_strategies)}")
            else:
                print("  No strategies worked reliably - check system configuration")
        
        print("\n" + "="*60)
    
    def run_full_test_suite(self):
        """Run the complete test suite"""
        print("🧪 Windows Injection Strategy Debug Suite")
        print("=" * 50)
        
        all_results = {}
        
        # Check availability
        all_results['availability'] = self.check_availability()
        
        # Basic injection test
        all_results['basic'] = self.test_basic_injection()
        
        # Special character test
        all_results['special_chars'] = self.test_special_characters()
        
        # Performance test (optional)
        print("\n❓ Run performance test? (y/n): ", end="")
        if input().lower().startswith('y'):
            all_results['performance'] = self.test_performance()
        
        # Application-specific test (optional)
        print("\n❓ Run application-specific test? (y/n): ", end="")
        if input().lower().startswith('y'):
            all_results['app_specific'] = self.test_application_specific()
        
        # Generate report
        self.generate_report(all_results)
        
        return all_results


def main():
    """Main function to run the debug suite"""
    if sys.platform != 'win32':
        print("❌ This debug tool is for Windows only")
        return
    
    print("🚀 Starting Windows Injection Debug Suite")
    print("Make sure you have text applications ready for testing!")
    print("Recommended: Notepad, browser, VS Code, terminal")
    
    debugger = WindowsInjectionDebugger()
    
    # Interactive menu
    while True:
        print("\n" + "="*50)
        print("WINDOWS INJECTION DEBUG MENU")
        print("="*50)
        print("1. Check Strategy Availability")
        print("2. Test Basic Injection")
        print("3. Test Special Characters")
        print("4. Test Performance")
        print("5. Test Application-Specific")
        print("6. Run Full Test Suite")
        print("7. Exit")
        print("-"*50)
        
        choice = input("Select option (1-7): ").strip()
        
        if choice == '1':
            debugger.check_availability()
        elif choice == '2':
            debugger.test_basic_injection()
        elif choice == '3':
            debugger.test_special_characters()
        elif choice == '4':
            debugger.test_performance()
        elif choice == '5':
            debugger.test_application_specific()
        elif choice == '6':
            debugger.run_full_test_suite()
        elif choice == '7':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option, please try again")


if __name__ == "__main__":
    main()