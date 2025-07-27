"""Enhanced dictation system with improved text injection

This module provides an enhanced version of the dictation system that uses
the improved text injection strategies for better reliability and performance.
"""

import time
import threading
from typing import Optional, Callable
from .dictation import SimpleDictation
from .text_injection_enhanced import EnhancedTextInjectionManager, InjectionResult
from .config import InjectionConfig
from .logger import setup_logger
from .constants import LogEmoji

logger = setup_logger(__name__)


class EnhancedDictationSystem(SimpleDictation):
    """Enhanced dictation system with improved text injection"""
    
    def __init__(self, 
                 model_name: str = "nvidia/parakeet-tdt-1.1b",
                 device_index: Optional[int] = None,
                 config: Optional[InjectionConfig] = None):
        
        # Initialize enhanced text injection manager
        self.injection_manager = EnhancedTextInjectionManager(config)
        
        # Initialize base dictation system
        super().__init__(model_name, device_index)
        
        # Enhanced features
        self.injection_stats = {
            'total_injections': 0,
            'successful_injections': 0,
            'failed_injections': 0,
            'strategy_usage': {}
        }
        
        # Override the text output callback
        self.processor.set_text_output_callback(self._enhanced_text_output)
        
        logger.info(f"{LogEmoji.SUCCESS} Enhanced dictation system initialized")
    
    def _enhanced_text_output(self, text: str):
        """Enhanced text output with improved injection and statistics"""
        if not text or not text.strip():
            return
        
        logger.debug(f"{LogEmoji.INFO} Processing text output: '{text}'")
        
        # Update statistics
        self.injection_stats['total_injections'] += 1
        
        # Attempt injection
        result = self.injection_manager.inject_text(text)
        
        # Update statistics based on result
        if result.success:
            self.injection_stats['successful_injections'] += 1
            
            # Track strategy usage
            strategy = result.strategy_used
            if strategy not in self.injection_stats['strategy_usage']:
                self.injection_stats['strategy_usage'][strategy] = 0
            self.injection_stats['strategy_usage'][strategy] += 1
            
            logger.info(f"{LogEmoji.SUCCESS} Text injected successfully using {strategy} "
                       f"(took {result.time_taken:.3f}s)")
        else:
            self.injection_stats['failed_injections'] += 1
            logger.warning(f"{LogEmoji.WARNING} Text injection failed: {result.error_message}")
            
            # Fallback to console display
            self._fallback_text_display(text)
    
    def _fallback_text_display(self, text: str):
        """Fallback text display when injection fails"""
        print(f"\n{LogEmoji.WARNING} DICTATION OUTPUT (injection failed): {text}")
        print(f"   Please copy and paste this text manually.")
    
    def get_injection_statistics(self) -> dict:
        """Get detailed injection statistics"""
        stats = self.injection_stats.copy()
        
        # Add performance stats from injection manager
        performance_stats = self.injection_manager.get_performance_stats()
        stats['strategy_performance'] = performance_stats
        
        # Calculate success rate
        total = stats['total_injections']
        if total > 0:
            stats['success_rate'] = stats['successful_injections'] / total
        else:
            stats['success_rate'] = 0.0
        
        # Add available strategies
        stats['available_strategies'] = self.injection_manager.get_available_strategies()
        
        return stats
    
    def print_injection_statistics(self):
        """Print detailed injection statistics"""
        stats = self.get_injection_statistics()
        
        print(f"\n{LogEmoji.INFO} === INJECTION STATISTICS ===")
        print(f"Total injections: {stats['total_injections']}")
        print(f"Successful: {stats['successful_injections']}")
        print(f"Failed: {stats['failed_injections']}")
        print(f"Success rate: {stats['success_rate']:.1%}")
        
        if stats['strategy_usage']:
            print(f"\n{LogEmoji.INFO} Strategy usage:")
            for strategy, count in stats['strategy_usage'].items():
                percentage = count / stats['total_injections'] * 100
                print(f"  {strategy}: {count} ({percentage:.1f}%)")
        
        if stats['strategy_performance']:
            print(f"\n{LogEmoji.INFO} Strategy performance:")
            for strategy, perf in stats['strategy_performance'].items():
                print(f"  {strategy}:")
                print(f"    Success rate: {perf['success_rate']:.1%}")
                print(f"    Avg time: {perf['avg_time']:.3f}s")
                print(f"    Total attempts: {perf['total_attempts']}")
                if perf['consecutive_failures'] > 0:
                    print(f"    Consecutive failures: {perf['consecutive_failures']}")
        
        print(f"\n{LogEmoji.INFO} Available strategies: {', '.join(stats['available_strategies'])}")
    
    def reset_injection_statistics(self):
        """Reset injection statistics"""
        self.injection_stats = {
            'total_injections': 0,
            'successful_injections': 0,
            'failed_injections': 0,
            'strategy_usage': {}
        }
        self.injection_manager.reset_performance_stats()
        logger.info(f"{LogEmoji.INFO} Injection statistics reset")
    
    def set_strategy_order(self, strategy_order: list):
        """Set custom strategy order for testing"""
        self.injection_manager.force_strategy_order(strategy_order)
        logger.info(f"{LogEmoji.INFO} Strategy order set to: {strategy_order}")
    
    def clear_strategy_order(self):
        """Clear custom strategy order"""
        self.injection_manager.clear_forced_order()
        logger.info(f"{LogEmoji.INFO} Strategy order cleared (using automatic optimization)")
    
    def test_injection_strategies(self, test_text: str = "Test injection"):
        """Test all available injection strategies"""
        logger.info(f"{LogEmoji.INFO} Testing injection strategies with: '{test_text}'")
        
        available_strategies = self.injection_manager.get_available_strategies()
        results = {}
        
        for strategy in available_strategies:
            logger.info(f"{LogEmoji.INFO} Testing {strategy}...")
            
            # Force this strategy temporarily
            self.injection_manager.force_strategy_order([strategy])
            
            # Test injection
            result = self.injection_manager.inject_text(test_text)
            results[strategy] = result
            
            status = "✓" if result.success else "✗"
            time_info = f" ({result.time_taken:.3f}s)" if result.success else ""
            error_info = f" - {result.error_message}" if result.error_message else ""
            
            print(f"  {status} {strategy}{time_info}{error_info}")
            
            # Small delay between tests
            time.sleep(0.5)
        
        # Clear forced order
        self.injection_manager.clear_forced_order()
        
        return results
    
    def start_with_injection_monitoring(self):
        """Start dictation with enhanced injection monitoring"""
        # Start a monitoring thread
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._injection_monitor, daemon=True)
        self.monitoring_thread.start()
        
        # Start normal dictation
        self.start()
    
    def _injection_monitor(self):
        """Monitor injection performance and provide periodic reports"""
        last_report_time = time.time()
        report_interval = 30  # Report every 30 seconds
        
        while self.monitoring_active and self.is_running:
            time.sleep(5)  # Check every 5 seconds
            
            current_time = time.time()
            if current_time - last_report_time >= report_interval:
                stats = self.get_injection_statistics()
                
                if stats['total_injections'] > 0:
                    logger.info(f"{LogEmoji.INFO} Injection monitoring report:")
                    logger.info(f"  Total: {stats['total_injections']}, "
                               f"Success rate: {stats['success_rate']:.1%}")
                    
                    # Report on strategy performance
                    if stats['strategy_performance']:
                        best_strategy = max(stats['strategy_performance'].items(),
                                          key=lambda x: x[1]['success_rate'])
                        logger.info(f"  Best strategy: {best_strategy[0]} "
                                   f"({best_strategy[1]['success_rate']:.1%})")
                
                last_report_time = current_time
    
    def stop(self):
        """Stop dictation and monitoring"""
        self.monitoring_active = False
        super().stop()
        
        # Print final statistics
        if hasattr(self, 'injection_stats') and self.injection_stats['total_injections'] > 0:
            print(f"\n{LogEmoji.INFO} Final injection statistics:")
            self.print_injection_statistics()


# Convenience function for easy usage
def create_enhanced_dictation_system(model_name: str = "nvidia/parakeet-tdt-1.1b",
                                    device_index: Optional[int] = None,
                                    config: Optional[InjectionConfig] = None) -> EnhancedDictationSystem:
    """Create an enhanced dictation system"""
    return EnhancedDictationSystem(model_name, device_index, config)


# Main function for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Dictation System")
    parser.add_argument("--test-injection", action="store_true",
                       help="Test injection strategies before starting")
    parser.add_argument("--stats-interval", type=int, default=30,
                       help="Statistics reporting interval (seconds)")
    parser.add_argument("--device", type=int, help="Audio device index")
    
    args = parser.parse_args()
    
    # Create enhanced dictation system
    system = create_enhanced_dictation_system(device_index=args.device)
    
    # Test injection if requested
    if args.test_injection:
        print(f"{LogEmoji.INFO} Testing injection strategies...")
        system.test_injection_strategies()
        print(f"\n{LogEmoji.INFO} Test complete. Starting dictation...")
    
    try:
        # Start with monitoring
        system.start_with_injection_monitoring()
        
        # Keep running until interrupted
        while system.is_running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{LogEmoji.INFO} Stopping dictation...")
        system.stop()
    except Exception as e:
        print(f"\n{LogEmoji.ERROR} Error: {e}")
        system.stop()