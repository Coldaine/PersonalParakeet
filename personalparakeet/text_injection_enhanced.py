"""Enhanced text injection system with improved strategies and optimizations

This module provides an enhanced version of the text injection system with:
- Improved Windows injection strategies
- Better application-specific optimizations
- Enhanced retry mechanisms
- Performance tuning for real-time dictation
"""

import time
import platform
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from .config import InjectionConfig
from .logger import setup_logger
from .constants import LogEmoji

logger = setup_logger(__name__)


@dataclass
class InjectionResult:
    """Result of an injection attempt"""
    success: bool
    strategy_used: str
    time_taken: float
    error_message: Optional[str] = None
    retry_count: int = 0


class EnhancedTextInjectionManager:
    """Enhanced text injection manager with improved strategies and optimizations"""
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        self.config = config if config is not None else InjectionConfig()
        self.strategies: Dict[str, any] = {}
        self.strategy_performance: Dict[str, Dict] = {}
        self.app_detector = None
        self.fallback_display: Optional[Callable[[str], None]] = None
        self._init_components()
    
    def _init_components(self):
        """Initialize all components"""
        self._init_app_detector()
        self._init_strategies()
        self._init_performance_tracking()
    
    def _init_app_detector(self):
        """Initialize application detector"""
        try:
            from .application_detection import ApplicationDetector
            self.app_detector = ApplicationDetector()
            logger.info(f"{LogEmoji.SUCCESS} Application detector initialized")
        except ImportError as e:
            logger.warning(f"{LogEmoji.WARNING} Application detection not available: {e}")
    
    def _init_strategies(self):
        """Initialize platform-specific injection strategies"""
        if platform.system() == 'Windows':
            self._init_windows_strategies()
        elif platform.system() == 'Linux':
            self._init_linux_strategies()
        else:
            self._init_basic_strategies()
    
    def _init_windows_strategies(self):
        """Initialize enhanced Windows strategies"""
        try:
            from .windows_injection_improved import (
                ImprovedWindowsUIAutomationStrategy,
                ImprovedWindowsKeyboardStrategy,
                ImprovedWindowsClipboardStrategy,
                ImprovedWindowsSendInputStrategy
            )
            
            self.strategies = {
                'ui_automation': ImprovedWindowsUIAutomationStrategy(self.config),
                'keyboard': ImprovedWindowsKeyboardStrategy(self.config),
                'clipboard': ImprovedWindowsClipboardStrategy(self.config),
                'send_input': ImprovedWindowsSendInputStrategy(self.config)
            }
            
            logger.info(f"{LogEmoji.SUCCESS} Enhanced Windows strategies initialized")
        except ImportError as e:
            logger.error(f"{LogEmoji.ERROR} Failed to initialize Windows strategies: {e}")
            self._init_basic_strategies()
    
    def _init_linux_strategies(self):
        """Initialize Linux strategies (fallback to existing implementation)"""
        try:
            from .linux_injection import LinuxXTestStrategy, LinuxClipboardStrategy
            
            self.strategies = {
                'xtest': LinuxXTestStrategy(self.config),
                'clipboard': LinuxClipboardStrategy(self.config)
            }
            
            logger.info(f"{LogEmoji.SUCCESS} Linux strategies initialized")
        except ImportError as e:
            logger.error(f"{LogEmoji.ERROR} Failed to initialize Linux strategies: {e}")
            self._init_basic_strategies()
    
    def _init_basic_strategies(self):
        """Initialize basic keyboard strategy as fallback"""
        try:
            from .basic_injection import BasicKeyboardStrategy
            self.strategies = {
                'basic_keyboard': BasicKeyboardStrategy(self.config)
            }
            logger.info(f"{LogEmoji.SUCCESS} Basic keyboard strategy initialized")
        except ImportError as e:
            logger.error(f"{LogEmoji.ERROR} Failed to initialize basic strategy: {e}")
    
    def _init_performance_tracking(self):
        """Initialize performance tracking for strategies"""
        for name in self.strategies.keys():
            self.strategy_performance[name] = {
                'total_attempts': 0,
                'successful_attempts': 0,
                'total_time': 0.0,
                'last_success': None,
                'consecutive_failures': 0
            }
    
    def inject_text(self, text: str, app_info: Optional[any] = None) -> InjectionResult:
        """Enhanced text injection with improved error handling and optimization"""
        start_time = time.time()
        
        # Auto-detect application if not provided
        if not app_info and self.app_detector:
            try:
                app_info = self.app_detector.detect_active_window()
                logger.debug(f"{LogEmoji.INFO} Detected application: {app_info.name}")
            except Exception as e:
                logger.warning(f"{LogEmoji.WARNING} Application detection failed: {e}")
        
        # Get optimized strategy order
        strategy_order = self._get_optimized_strategy_order(app_info)
        
        # Try each strategy with retry logic
        for strategy_name in strategy_order:
            if strategy_name not in self.strategies:
                continue
            
            strategy = self.strategies[strategy_name]
            
            # Check if strategy is available
            if not strategy.is_available():
                logger.debug(f"{LogEmoji.INFO} Strategy {strategy_name} not available")
                continue
            
            # Skip strategies with too many consecutive failures
            if self._should_skip_strategy(strategy_name):
                logger.debug(f"{LogEmoji.INFO} Skipping {strategy_name} due to consecutive failures")
                continue
            
            # Attempt injection with retry
            result = self._attempt_injection_with_retry(strategy, strategy_name, text, app_info)
            
            # Update performance metrics
            self._update_performance_metrics(strategy_name, result)
            
            if result.success:
                result.time_taken = time.time() - start_time
                logger.info(f"{LogEmoji.SUCCESS} Text injection successful with {strategy_name}")
                return result
        
        # All strategies failed - use fallback
        logger.warning(f"{LogEmoji.WARNING} All injection strategies failed")
        if self.fallback_display:
            self.fallback_display(text)
        
        return InjectionResult(
            success=False,
            strategy_used='none',
            time_taken=time.time() - start_time,
            error_message='All strategies failed'
        )
    
    def _get_optimized_strategy_order(self, app_info: Optional[any]) -> List[str]:
        """Get optimized strategy order based on application and performance"""
        if platform.system() == 'Windows':
            return self._get_windows_optimized_order(app_info)
        elif platform.system() == 'Linux':
            return self._get_linux_optimized_order(app_info)
        else:
            return list(self.strategies.keys())
    
    def _get_windows_optimized_order(self, app_info: Optional[any]) -> List[str]:
        """Get optimized Windows strategy order"""
        base_order = ['ui_automation', 'keyboard', 'clipboard', 'send_input']
        
        # Application-specific optimizations
        if app_info:
            app_optimizations = {
                'EDITOR': ['clipboard', 'ui_automation', 'keyboard', 'send_input'],
                'IDE': ['clipboard', 'ui_automation', 'keyboard', 'send_input'],
                'TERMINAL': ['keyboard', 'send_input', 'ui_automation'],
                'BROWSER': ['keyboard', 'ui_automation', 'send_input'],
                'OFFICE': ['ui_automation', 'clipboard', 'keyboard', 'send_input']
            }
            
            app_type = getattr(app_info, 'app_type', None)
            if app_type and hasattr(app_type, 'name'):
                base_order = app_optimizations.get(app_type.name, base_order)
        
        # Performance-based reordering
        return self._reorder_by_performance(base_order)
    
    def _get_linux_optimized_order(self, app_info: Optional[any]) -> List[str]:
        """Get optimized Linux strategy order"""
        base_order = ['xtest', 'clipboard']
        return self._reorder_by_performance(base_order)
    
    def _reorder_by_performance(self, base_order: List[str]) -> List[str]:
        """Reorder strategies based on recent performance"""
        # Sort by success rate, then by average time
        available_strategies = [name for name in base_order if name in self.strategies]
        
        def strategy_score(name: str) -> float:
            perf = self.strategy_performance.get(name, {})
            attempts = perf.get('total_attempts', 0)
            if attempts == 0:
                return 1.0  # New strategies get high priority
            
            success_rate = perf.get('successful_attempts', 0) / attempts
            avg_time = perf.get('total_time', 0.1) / attempts
            
            # Penalize strategies with consecutive failures
            consecutive_failures = perf.get('consecutive_failures', 0)
            failure_penalty = max(0, 1 - (consecutive_failures * 0.1))
            
            # Score: success rate * speed * failure penalty
            return success_rate * (1 / avg_time) * failure_penalty
        
        # Sort by score (higher is better)
        return sorted(available_strategies, key=strategy_score, reverse=True)
    
    def _should_skip_strategy(self, strategy_name: str) -> bool:
        """Check if strategy should be skipped due to consecutive failures"""
        perf = self.strategy_performance.get(strategy_name, {})
        consecutive_failures = perf.get('consecutive_failures', 0)
        return consecutive_failures >= 3  # Skip after 3 consecutive failures
    
    def _attempt_injection_with_retry(self, strategy: any, strategy_name: str, 
                                    text: str, app_info: Optional[any]) -> InjectionResult:
        """Attempt injection with retry logic"""
        max_retries = getattr(self.config, 'max_clipboard_retries', 3)
        
        for attempt in range(max_retries):
            start_time = time.time()
            
            try:
                logger.debug(f"{LogEmoji.INFO} Attempting {strategy_name} (attempt {attempt + 1})")
                
                # Add small delay between retries
                if attempt > 0:
                    time.sleep(getattr(self.config, 'clipboard_retry_delay', 0.1))
                
                success = strategy.inject(text, app_info)
                
                return InjectionResult(
                    success=success,
                    strategy_used=strategy_name,
                    time_taken=time.time() - start_time,
                    retry_count=attempt
                )
                
            except Exception as e:
                logger.debug(f"{LogEmoji.WARNING} {strategy_name} attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:  # Last attempt
                    return InjectionResult(
                        success=False,
                        strategy_used=strategy_name,
                        time_taken=time.time() - start_time,
                        error_message=str(e),
                        retry_count=attempt + 1
                    )
    
    def _update_performance_metrics(self, strategy_name: str, result: InjectionResult):
        """Update performance metrics for a strategy"""
        if strategy_name not in self.strategy_performance:
            return
        
        perf = self.strategy_performance[strategy_name]
        perf['total_attempts'] += 1
        perf['total_time'] += result.time_taken
        
        if result.success:
            perf['successful_attempts'] += 1
            perf['last_success'] = time.time()
            perf['consecutive_failures'] = 0
        else:
            perf['consecutive_failures'] += 1
    
    def get_performance_stats(self) -> Dict[str, Dict]:
        """Get performance statistics for all strategies"""
        stats = {}
        
        for name, perf in self.strategy_performance.items():
            attempts = perf['total_attempts']
            if attempts > 0:
                stats[name] = {
                    'success_rate': perf['successful_attempts'] / attempts,
                    'avg_time': perf['total_time'] / attempts,
                    'total_attempts': attempts,
                    'consecutive_failures': perf['consecutive_failures']
                }
        
        return stats
    
    def reset_performance_stats(self):
        """Reset performance statistics"""
        self._init_performance_tracking()
        logger.info(f"{LogEmoji.INFO} Performance statistics reset")
    
    def set_fallback_display(self, callback: Callable[[str], None]):
        """Set fallback display callback"""
        self.fallback_display = callback
    
    def get_available_strategies(self) -> List[str]:
        """Get list of available strategies"""
        return [name for name, strategy in self.strategies.items() 
                if strategy.is_available()]
    
    def force_strategy_order(self, strategy_order: List[str]):
        """Force a specific strategy order (for testing)"""
        self._forced_order = strategy_order
    
    def clear_forced_order(self):
        """Clear forced strategy order"""
        self._forced_order = None


# Convenience function for backward compatibility
def create_enhanced_injection_manager(config: Optional[InjectionConfig] = None) -> EnhancedTextInjectionManager:
    """Create an enhanced text injection manager"""
    return EnhancedTextInjectionManager(config)