"""
Enhanced Text Injection Manager for PersonalParakeet v3
Complete port of v2 enhanced injection with all strategies and performance tracking
"""

import logging
import time
import threading
import platform
from typing import Optional, List, Dict, Any, Callable, Tuple
from enum import Enum, auto
from dataclasses import dataclass

from .application_detector import EnhancedApplicationDetector, ApplicationInfo, ApplicationProfile

logger = logging.getLogger(__name__)


class InjectionStrategy(Enum):
    """Available injection strategies"""

    UI_AUTOMATION = auto()  # Highest priority - most reliable
    KEYBOARD = auto()  # Fast and simple
    CLIPBOARD = auto()  # Good for large text
    WIN32_SENDINPUT = auto()  # Low-level fallback


@dataclass
class InjectionResult:
    """Result of an injection attempt"""

    success: bool
    strategy_used: str
    time_taken: float
    error_message: Optional[str] = None
    retry_count: int = 0


class PerformanceTracker:
    """Track injection performance statistics"""

    def __init__(self):
        self.stats = {}
        self.lock = threading.Lock()

    def record_attempt(self, strategy_name: str, result: InjectionResult):
        """Record an injection attempt"""
        with self.lock:
            if strategy_name not in self.stats:
                self.stats[strategy_name] = {
                    "total_attempts": 0,
                    "successful_attempts": 0,
                    "total_time": 0.0,
                    "last_success": None,
                    "consecutive_failures": 0,
                    "average_time": 0.0,
                    "success_rate": 0.0,
                }

            stat = self.stats[strategy_name]
            stat["total_attempts"] += 1
            stat["total_time"] += result.time_taken

            if result.success:
                stat["successful_attempts"] += 1
                stat["last_success"] = time.time()
                stat["consecutive_failures"] = 0
            else:
                stat["consecutive_failures"] += 1

            # Update calculated fields
            stat["average_time"] = stat["total_time"] / stat["total_attempts"]
            stat["success_rate"] = stat["successful_attempts"] / stat["total_attempts"]

    def get_stats(self) -> Dict[str, Dict]:
        """Get all performance statistics"""
        with self.lock:
            return self.stats.copy()

    def get_strategy_score(self, strategy_name: str) -> float:
        """Calculate a performance score for a strategy"""
        with self.lock:
            if strategy_name not in self.stats:
                return 1.0  # New strategies get high priority

            stat = self.stats[strategy_name]

            # Skip strategies with too many consecutive failures
            if stat["consecutive_failures"] >= 3:
                return 0.0

            # Score based on success rate and speed
            success_rate = stat["success_rate"]
            avg_time = stat["average_time"] or 0.1

            # Penalize consecutive failures
            failure_penalty = max(0, 1 - (stat["consecutive_failures"] * 0.2))

            # Score: success rate * speed * failure penalty
            return success_rate * (1 / avg_time) * failure_penalty

    def reset_stats(self):
        """Reset all statistics"""
        with self.lock:
            self.stats.clear()


class EnhancedWindowsTextInjector:
    """Enhanced Windows text injection with all v2 strategies"""

    def __init__(self):
        self.strategies = {}
        self.strategy_order = []
        self.last_injection_time = 0
        self.performance_tracker = PerformanceTracker()
        self._init_all_strategies()

    def _init_all_strategies(self):
        """Initialize all injection strategies"""
        # UI Automation strategy
        self._init_ui_automation()

        # Keyboard strategy
        self._init_keyboard()

        # Enhanced clipboard strategy
        self._init_enhanced_clipboard()

        # Win32 SendInput strategy
        self._init_win32_sendinput()

        # Set default strategy order
        self.strategy_order = [
            InjectionStrategy.UI_AUTOMATION,
            InjectionStrategy.KEYBOARD,
            InjectionStrategy.CLIPBOARD,
            InjectionStrategy.WIN32_SENDINPUT,
        ]

    def _init_ui_automation(self):
        """Initialize UI Automation strategy"""
        try:
            import comtypes.client
            from comtypes import automation

            self.uia = comtypes.client.CreateObject(
                "{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=automation.IUIAutomation
            )

            self.pattern_cache = {
                "text": 10014,  # UIA_TextPatternId
                "value": 10002,  # UIA_ValuePatternId
                "legacy": 10018,  # UIA_LegacyIAccessiblePatternId
            }

            self.strategies[InjectionStrategy.UI_AUTOMATION] = self._inject_ui_automation
            logger.info("✓ UI Automation strategy initialized")
        except Exception as e:
            logger.debug(f"UI Automation not available: {e}")

    def _init_keyboard(self):
        """Initialize keyboard strategy"""
        try:
            import keyboard

            self.strategies[InjectionStrategy.KEYBOARD] = self._inject_keyboard
            logger.info("✓ Keyboard strategy initialized")
        except ImportError:
            logger.warning("Keyboard library not available")

    def _init_enhanced_clipboard(self):
        """Initialize enhanced clipboard strategy with format preservation"""
        self.clipboard_available = False
        self.clipboard_lock = threading.Lock()

        if platform.system() == "Windows":
            try:
                import win32clipboard

                self.win32clipboard = win32clipboard
                self.clipboard_available = True
                self.use_win32clipboard = True
                logger.info("✓ Win32 clipboard strategy initialized")
            except ImportError:
                pass

        if not self.clipboard_available:
            try:
                import pyperclip

                self.pyperclip = pyperclip
                self.clipboard_available = True
                self.use_win32clipboard = False
                logger.info("✓ Pyperclip clipboard strategy initialized")
            except ImportError:
                logger.warning("No clipboard library available")

        if self.clipboard_available:
            self.strategies[InjectionStrategy.CLIPBOARD] = self._inject_enhanced_clipboard

    def _init_win32_sendinput(self):
        """Initialize Win32 SendInput strategy"""
        try:
            import ctypes
            from ctypes import wintypes

            self.user32 = ctypes.windll.user32
            self.strategies[InjectionStrategy.WIN32_SENDINPUT] = self._inject_win32_sendinput
            logger.info("✓ Win32 SendInput strategy initialized")
        except Exception as e:
            logger.debug(f"Win32 SendInput not available: {e}")

    def inject(
        self,
        text: str,
        strategy_order: Optional[List[str]] = None,
        app_info: Optional[ApplicationInfo] = None,
    ) -> InjectionResult:
        """
        Inject text using the best available strategy

        Args:
            text: Text to inject
            strategy_order: Optional custom strategy order
            app_info: Optional application information

        Returns:
            InjectionResult with details of the injection
        """
        if not text.strip():
            return InjectionResult(
                success=False,
                strategy_used="none",
                time_taken=0,
                error_message="Empty text provided",
            )

        # Add space for natural dictation flow
        text_to_inject = text.strip() + " "

        # Rate limiting
        current_time = time.time()
        if current_time - self.last_injection_time < 0.02:
            time.sleep(0.02)

        # Determine strategy order
        if strategy_order:
            strategies_to_try = [self._get_strategy_enum(s) for s in strategy_order]
        else:
            strategies_to_try = self._get_optimized_strategy_order(app_info)

        # Try each strategy
        for strategy in strategies_to_try:
            if strategy not in self.strategies:
                continue

            start_time = time.time()
            try:
                logger.debug(f"Attempting injection with {strategy.name}")

                # Apply app-specific delays if available
                if app_info:
                    self._apply_app_delays(app_info)

                success = self.strategies[strategy](text_to_inject, app_info)

                result = InjectionResult(
                    success=success,
                    strategy_used=strategy.name,
                    time_taken=time.time() - start_time,
                )

                # Record performance
                self.performance_tracker.record_attempt(strategy.name, result)

                if success:
                    self.last_injection_time = time.time()
                    logger.info(f"✓ Text injected successfully using {strategy.name}")
                    return result

            except Exception as e:
                logger.debug(f"Strategy {strategy.name} failed: {e}")
                result = InjectionResult(
                    success=False,
                    strategy_used=strategy.name,
                    time_taken=time.time() - start_time,
                    error_message=str(e),
                )
                self.performance_tracker.record_attempt(strategy.name, result)
                continue

        # All strategies failed
        return InjectionResult(
            success=False,
            strategy_used="none",
            time_taken=0,
            error_message="All injection strategies failed",
        )

    def _get_strategy_enum(self, strategy_name: str) -> Optional[InjectionStrategy]:
        """Convert strategy name to enum"""
        strategy_map = {
            "ui_automation": InjectionStrategy.UI_AUTOMATION,
            "keyboard": InjectionStrategy.KEYBOARD,
            "clipboard": InjectionStrategy.CLIPBOARD,
            "win32_sendinput": InjectionStrategy.WIN32_SENDINPUT,
        }
        return strategy_map.get(strategy_name)

    def _get_optimized_strategy_order(
        self, app_info: Optional[ApplicationInfo]
    ) -> List[InjectionStrategy]:
        """Get performance-optimized strategy order"""
        # Start with default or app-specific order
        if app_info:
            # Application-specific order (from profile)
            base_order = self.strategy_order
        else:
            base_order = self.strategy_order

        # Sort by performance score
        return sorted(
            base_order,
            key=lambda s: self.performance_tracker.get_strategy_score(s.name),
            reverse=True,
        )

    def _apply_app_delays(self, app_info: ApplicationInfo):
        """Apply application-specific timing delays"""
        # This is a placeholder for app-specific timing
        # In a full implementation, this would use the app profile
        pass

    def _inject_ui_automation(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Enhanced UI Automation injection with multiple patterns"""
        if not hasattr(self, "uia") or not self.uia:
            return False

        try:
            # Get focused element with retry
            focused = None
            for attempt in range(3):
                try:
                    focused = self.uia.GetFocusedElement()
                    if focused:
                        break
                    time.sleep(0.01)
                except:
                    pass

            if not focused:
                return False

            # Try different patterns
            patterns = [
                ("text", self._try_text_pattern),
                ("value", self._try_value_pattern),
                ("legacy", self._try_legacy_pattern),
            ]

            for pattern_name, pattern_func in patterns:
                try:
                    if pattern_func(focused, text):
                        return True
                except Exception as e:
                    logger.debug(f"{pattern_name} pattern failed: {e}")
                    continue

            # Fallback to keyboard if all patterns fail
            return self._ui_automation_keyboard_fallback(focused, text)

        except Exception as e:
            logger.debug(f"UI Automation injection failed: {e}")
            return False

    def _try_text_pattern(self, element, text: str) -> bool:
        """Try TextPattern for rich text controls"""
        text_pattern = element.GetCurrentPattern(self.pattern_cache["text"])
        if text_pattern:
            doc_range = text_pattern.DocumentRange
            if doc_range:
                try:
                    selection = text_pattern.GetSelection()
                    if selection and len(selection) > 0:
                        selection[0].InsertText(text)
                    else:
                        doc_range.InsertText(text)
                    return True
                except:
                    doc_range.InsertText(text)
                    return True
        return False

    def _try_value_pattern(self, element, text: str) -> bool:
        """Try ValuePattern for simple text inputs"""
        value_pattern = element.GetCurrentPattern(self.pattern_cache["value"])
        if value_pattern:
            try:
                if hasattr(value_pattern, "CurrentIsReadOnly") and value_pattern.CurrentIsReadOnly:
                    return False
                current = value_pattern.CurrentValue or ""
                value_pattern.SetValue(current + text)
                return True
            except:
                pass
        return False

    def _try_legacy_pattern(self, element, text: str) -> bool:
        """Try LegacyIAccessiblePattern for older controls"""
        legacy_pattern = element.GetCurrentPattern(self.pattern_cache["legacy"])
        if legacy_pattern:
            try:
                legacy_pattern.SetValue(text)
                return True
            except:
                pass
        return False

    def _ui_automation_keyboard_fallback(self, element, text: str) -> bool:
        """Fallback to keyboard after focusing element"""
        try:
            element.SetFocus()
            time.sleep(0.01)
            import keyboard

            keyboard.write(text)
            return True
        except:
            return False

    def _inject_keyboard(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Enhanced keyboard injection with rate limiting"""
        try:
            import keyboard

            # Small delay for focus acquisition
            time.sleep(0.01)

            # Try different methods
            try:
                keyboard.write(text)
                return True
            except:
                # Fallback to character-by-character
                for char in text:
                    keyboard.write(char)
                    time.sleep(0.001)
                return True

        except Exception as e:
            logger.debug(f"Keyboard injection failed: {e}")
            return False

    def _inject_enhanced_clipboard(
        self, text: str, app_info: Optional[ApplicationInfo] = None
    ) -> bool:
        """Enhanced clipboard injection with format preservation"""
        if not self.clipboard_available:
            return False

        with self.clipboard_lock:
            try:
                # Save original clipboard with format
                original_content, original_formats = self._save_clipboard_with_format()

                # Set new content
                if not self._set_clipboard_content(text):
                    return False

                # Perform paste with retry
                success = self._paste_with_retry()

                # Restore original clipboard
                self._restore_clipboard_with_format(original_content, original_formats)

                return success

            except Exception as e:
                logger.debug(f"Enhanced clipboard injection failed: {e}")
                return False

    def _save_clipboard_with_format(self) -> Tuple[Any, Any]:
        """Save clipboard content with format information"""
        try:
            if self.use_win32clipboard:
                self.win32clipboard.OpenClipboard()
                try:
                    formats = []
                    content = None

                    # Try to preserve HTML format
                    html_format = self.win32clipboard.RegisterClipboardFormat("HTML Format")
                    if self.win32clipboard.IsClipboardFormatAvailable(html_format):
                        html_content = self.win32clipboard.GetClipboardData(html_format)
                        formats.append((html_format, html_content))

                    # Get Unicode text
                    if self.win32clipboard.IsClipboardFormatAvailable(
                        self.win32clipboard.CF_UNICODETEXT
                    ):
                        content = self.win32clipboard.GetClipboardData(
                            self.win32clipboard.CF_UNICODETEXT
                        )
                        formats.append((self.win32clipboard.CF_UNICODETEXT, content))

                    return content or "", formats
                finally:
                    self.win32clipboard.CloseClipboard()
            else:
                # Pyperclip doesn't support formats
                return self.pyperclip.paste(), None
        except:
            return "", None

    def _set_clipboard_content(self, text: str) -> bool:
        """Set clipboard content"""
        try:
            if self.use_win32clipboard:
                self.win32clipboard.OpenClipboard()
                try:
                    self.win32clipboard.EmptyClipboard()
                    self.win32clipboard.SetClipboardData(self.win32clipboard.CF_UNICODETEXT, text)
                finally:
                    self.win32clipboard.CloseClipboard()
            else:
                self.pyperclip.copy(text)

            time.sleep(0.01)
            return True
        except:
            return False

    def _paste_with_retry(self, max_retries: int = 3) -> bool:
        """Perform paste operation with retry"""
        for attempt in range(max_retries):
            try:
                # Try keyboard library first
                try:
                    import keyboard

                    keyboard.send("ctrl+v")
                    time.sleep(0.05)
                    return True
                except:
                    pass

                # Try Win32 API
                if hasattr(self, "user32"):
                    self._send_key_combination([0x11, 0x56])  # Ctrl + V
                    time.sleep(0.05)
                    return True

                if attempt < max_retries - 1:
                    time.sleep(0.1)

            except Exception as e:
                logger.debug(f"Paste attempt {attempt + 1} failed: {e}")

        return False

    def _restore_clipboard_with_format(self, content: Any, formats: Any):
        """Restore clipboard content with original format"""
        try:
            if self.use_win32clipboard and formats:
                self.win32clipboard.OpenClipboard()
                try:
                    self.win32clipboard.EmptyClipboard()
                    for format_id, data in formats:
                        self.win32clipboard.SetClipboardData(format_id, data)
                finally:
                    self.win32clipboard.CloseClipboard()
            elif content:
                self._set_clipboard_content(content)
        except:
            pass

    def _inject_win32_sendinput(
        self, text: str, app_info: Optional[ApplicationInfo] = None
    ) -> bool:
        """Enhanced Win32 SendInput with Unicode support"""
        if not hasattr(self, "user32"):
            return False

        try:
            import ctypes
            from ctypes import wintypes, Structure, Union

            # Define INPUT structures
            class KEYBDINPUT(Structure):
                _fields_ = [
                    ("wVk", wintypes.WORD),
                    ("wScan", wintypes.WORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
                ]

            class INPUT(Structure):
                class _INPUT(Union):
                    _fields_ = [("ki", KEYBDINPUT)]

                _fields_ = [("type", wintypes.DWORD), ("union", _INPUT)]

            INPUT_KEYBOARD = 1
            KEYEVENTF_UNICODE = 0x0004
            KEYEVENTF_KEYUP = 0x0002

            # Focus delay
            time.sleep(0.01)

            # Send each character
            for char in text:
                # Key down
                input_down = INPUT()
                input_down.type = INPUT_KEYBOARD
                input_down.union.ki.wVk = 0
                input_down.union.ki.wScan = ord(char)
                input_down.union.ki.dwFlags = KEYEVENTF_UNICODE
                input_down.union.ki.time = 0
                input_down.union.ki.dwExtraInfo = None

                # Key up
                input_up = INPUT()
                input_up.type = INPUT_KEYBOARD
                input_up.union.ki.wVk = 0
                input_up.union.ki.wScan = ord(char)
                input_up.union.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
                input_up.union.ki.time = 0
                input_up.union.ki.dwExtraInfo = None

                # Send inputs
                self.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(INPUT))
                self.user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(INPUT))

                time.sleep(0.001)

            return True

        except Exception as e:
            logger.debug(f"Win32 SendInput injection failed: {e}")
            return False

    def _send_key_combination(self, key_codes: List[int]):
        """Send a key combination using Win32 API"""
        for key_code in key_codes:
            self.user32.keybd_event(key_code, 0, 0, 0)
            time.sleep(0.001)

        for key_code in reversed(key_codes):
            self.user32.keybd_event(key_code, 0, 2, 0)  # KEYEVENTF_KEYUP
            time.sleep(0.001)

    def get_performance_stats(self) -> Dict[str, Dict]:
        """Get performance statistics for all strategies"""
        return self.performance_tracker.get_stats()

    def reset_performance_stats(self):
        """Reset performance statistics"""
        self.performance_tracker.reset_stats()

    def is_strategy_available(self, strategy: InjectionStrategy) -> bool:
        """Check if a specific strategy is available"""
        return strategy in self.strategies


class EnhancedInjectionManager:
    """
    Enhanced injection manager for PersonalParakeet v3
    Complete port from v2 with all strategies and performance optimization
    """

    def __init__(self):
        self.injector = EnhancedWindowsTextInjector()
        self.app_detector = EnhancedApplicationDetector()
        self.injection_thread = None
        self.injection_lock = threading.Lock()
        self.injection_count = 0
        self.fallback_display_callback = None

        # Comprehensive performance stats
        self.performance_stats = {
            "total_injections": 0,
            "successful_injections": 0,
            "failed_injections": 0,
            "app_type_stats": {},
            "strategy_usage": {},
            "average_injection_time": 0.0,
            "last_injection_time": None,
        }

        logger.info("✓ Enhanced InjectionManager v3 initialized with all v2 strategies")

    def inject_text(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """
        Inject text with full v2 feature parity

        Args:
            text: Text to inject
            app_info: Optional application information

        Returns:
            True if injection succeeded, False otherwise
        """
        if not text or not text.strip():
            logger.warning("Attempted to inject empty text")
            return False

        with self.injection_lock:
            try:
                self.injection_count += 1
                self.performance_stats["total_injections"] += 1
                start_time = time.time()

                # Auto-detect application if not provided
                if not app_info:
                    app_info = self.app_detector.detect_current_application()

                if app_info:
                    logger.info(
                        f"Injecting text (#{self.injection_count}) into {app_info.name}: '{text.strip()[:50]}...'"
                    )

                    # Get optimized strategy order
                    strategy_order = self.app_detector.get_optimized_strategy_order(app_info)

                    # Update app type stats
                    app_type_name = app_info.app_type.name
                    self.performance_stats["app_type_stats"][app_type_name] = (
                        self.performance_stats["app_type_stats"].get(app_type_name, 0) + 1
                    )
                else:
                    logger.info(
                        f"Injecting text (#{self.injection_count}) into unknown app: '{text.strip()[:50]}...'"
                    )
                    strategy_order = None

                # Perform injection
                result = self.injector.inject(text, strategy_order, app_info)

                # Update statistics
                self._update_stats(result, time.time() - start_time)

                if result.success:
                    logger.info(
                        f"✓ Injection #{self.injection_count} successful with {result.strategy_used} ({result.time_taken:.3f}s)"
                    )
                else:
                    logger.error(
                        f"❌ Injection #{self.injection_count} failed: {result.error_message}"
                    )
                    # Use fallback display if available
                    if self.fallback_display_callback:
                        self.fallback_display_callback(text)

                return result.success

            except Exception as e:
                logger.error(f"❌ Injection manager error: {e}")
                self.performance_stats["failed_injections"] += 1
                return False

    def inject_text_async(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text asynchronously (non-blocking)"""
        try:
            self.injection_thread = threading.Thread(
                target=self.inject_text, args=(text, app_info), daemon=True
            )
            self.injection_thread.start()
            return True
        except Exception as e:
            logger.error(f"Failed to start async injection: {e}")
            return False

    def _update_stats(self, result: InjectionResult, total_time: float):
        """Update comprehensive statistics"""
        if result.success:
            self.performance_stats["successful_injections"] += 1
        else:
            self.performance_stats["failed_injections"] += 1

        # Update strategy usage
        if result.strategy_used != "none":
            if result.strategy_used not in self.performance_stats["strategy_usage"]:
                self.performance_stats["strategy_usage"][result.strategy_used] = {
                    "attempts": 0,
                    "successes": 0,
                    "failures": 0,
                    "total_time": 0.0,
                }

            stats = self.performance_stats["strategy_usage"][result.strategy_used]
            stats["attempts"] += 1
            stats["total_time"] += result.time_taken

            if result.success:
                stats["successes"] += 1
            else:
                stats["failures"] += 1

        # Update average time
        total_inj = self.performance_stats["total_injections"]
        prev_avg = self.performance_stats["average_injection_time"]
        self.performance_stats["average_injection_time"] = (
            prev_avg * (total_inj - 1) + total_time
        ) / total_inj

        self.performance_stats["last_injection_time"] = time.time()

    def set_fallback_display(self, callback: Callable[[str], None]):
        """Set fallback display callback for when all strategies fail"""
        self.fallback_display_callback = callback

    def get_current_application(self) -> Optional[ApplicationInfo]:
        """Get information about the currently active application"""
        try:
            return self.app_detector.detect_current_application()
        except Exception as e:
            logger.error(f"Failed to detect current application: {e}")
            return None

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        success_rate = 0.0
        if self.performance_stats["total_injections"] > 0:
            success_rate = (
                self.performance_stats["successful_injections"]
                / self.performance_stats["total_injections"]
            ) * 100

        # Get strategy performance from injector
        strategy_performance = self.injector.get_performance_stats()

        return {
            "total_injections": self.performance_stats["total_injections"],
            "successful_injections": self.performance_stats["successful_injections"],
            "failed_injections": self.performance_stats["failed_injections"],
            "success_rate_percent": round(success_rate, 1),
            "average_injection_time_ms": round(
                self.performance_stats["average_injection_time"] * 1000, 1
            ),
            "app_type_distribution": self.performance_stats["app_type_stats"].copy(),
            "strategy_usage": self.performance_stats["strategy_usage"].copy(),
            "strategy_performance": strategy_performance,
            "detector_status": self.app_detector.get_detector_status(),
            "last_injection_time": self.performance_stats["last_injection_time"],
        }

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive injection manager status"""
        current_app = self.get_current_application()

        available_strategies = []
        for strategy in InjectionStrategy:
            if self.injector.is_strategy_available(strategy):
                available_strategies.append(strategy.name)

        status = {
            "injection_count": self.injection_count,
            "available_strategies": available_strategies,
            "current_application": {
                "name": current_app.name if current_app else "Unknown",
                "type": current_app.app_type.name if current_app else "UNKNOWN",
                "window_title": current_app.window_title if current_app else "",
            },
            "performance_stats": self.get_performance_stats(),
        }

        return status

    def reset_performance_stats(self):
        """Reset all performance statistics"""
        self.performance_stats = {
            "total_injections": 0,
            "successful_injections": 0,
            "failed_injections": 0,
            "app_type_stats": {},
            "strategy_usage": {},
            "average_injection_time": 0.0,
            "last_injection_time": None,
        }
        self.injector.reset_performance_stats()
        logger.info("Performance statistics reset")

    def force_strategy_order(self, strategy_order: List[str]):
        """Force a specific strategy order (for testing)"""
        # Convert string names to enum values
        enum_order = []
        for name in strategy_order:
            strategy = self.injector._get_strategy_enum(name)
            if strategy:
                enum_order.append(strategy)

        if enum_order:
            self.injector.strategy_order = enum_order
            logger.info(f"Forced strategy order: {[s.name for s in enum_order]}")


# Global instance for easy access
injection_manager = EnhancedInjectionManager()
