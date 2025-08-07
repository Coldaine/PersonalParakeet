"""
Enhanced text injection strategies for PersonalParakeet v3
Ported from v2 with improvements for single-process architecture
"""

import logging
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .application_detector import ApplicationInfo, ApplicationProfile

logger = logging.getLogger(__name__)


@dataclass
class InjectionResult:
    """Result of an injection attempt"""

    success: bool
    strategy_used: str
    time_taken: float
    error_message: Optional[str] = None
    retry_count: int = 0


class StrategyType(Enum):
    """Available injection strategy types"""

    UI_AUTOMATION = "ui_automation"
    KEYBOARD = "keyboard"
    CLIPBOARD = "clipboard"
    WIN32_SENDINPUT = "send_input"
    BASIC_KEYBOARD = "basic_keyboard"


class BaseInjectionStrategy:
    """Base class for all injection strategies"""

    def __init__(self, name: str):
        self.name = name
        self.config = {
            "key_delay": 0.001,
            "focus_delay": 0.01,
            "retry_count": 3,
            "retry_delay": 0.1,
        }

    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using this strategy"""
        raise NotImplementedError

    def is_available(self) -> bool:
        """Check if this strategy is available on the current system"""
        raise NotImplementedError

    def get_config(self) -> Dict[str, Any]:
        """Get strategy configuration"""
        return self.config

    def update_config(self, config: Dict[str, Any]):
        """Update strategy configuration"""
        self.config.update(config)


class EnhancedUIAutomationStrategy(BaseInjectionStrategy):
    """Enhanced Windows UI Automation strategy with fallback patterns"""

    def __init__(self):
        super().__init__(StrategyType.UI_AUTOMATION.value)
        self.uia = None
        self.pattern_cache = {}
        self._init_ui_automation()

    def _init_ui_automation(self):
        """Initialize Windows UI Automation COM objects"""
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

            logger.info("UI Automation strategy initialized")
        except Exception as e:
            logger.debug(f"UI Automation initialization failed: {e}")
            self.uia = None

    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using UI Automation with multiple fallback patterns"""
        if not self.uia:
            return False

        try:
            focused = self._get_focused_element()
            if not focused:
                return False

            patterns_to_try = [
                ("text", self._try_text_pattern),
                ("value", self._try_value_pattern),
                ("legacy", self._try_legacy_pattern),
                ("send_keys", self._try_send_keys_fallback),
            ]

            for pattern_name, pattern_func in patterns_to_try:
                try:
                    if pattern_func(focused, text):
                        return True
                except Exception as e:
                    logger.debug(f"UI Automation pattern {pattern_name} failed: {e}")
                    continue

            return False

        except Exception as e:
            logger.debug(f"UI Automation injection failed: {e}")
            return False

    def _get_focused_element(self):
        """Get currently focused element"""
        try:
            if self.uia:
                return self.uia.GetFocusedElement()
            return None
        except Exception:
            return None

    def _try_text_pattern(self, element, text: str) -> bool:
        """Try TextPattern for rich text controls"""
        try:
            text_pattern = element.GetCurrentPattern(self.pattern_cache["text"])
            if text_pattern:
                doc_range = text_pattern.DocumentRange
                if doc_range:
                    selection = text_pattern.GetSelection()
                    if selection and len(selection) > 0:
                        selection[0].InsertText(text + " ")
                    else:
                        doc_range.InsertText(text + " ")
                    return True
        except Exception:
            pass
        return False

    def _try_value_pattern(self, element, text: str) -> bool:
        """Try ValuePattern for simple text inputs"""
        try:
            value_pattern = element.GetCurrentPattern(self.pattern_cache["value"])
            if value_pattern:
                current = value_pattern.CurrentValue or ""
                new_value = current + text + " "
                value_pattern.SetValue(new_value)
                return True
        except Exception:
            pass
        return False

    def _try_legacy_pattern(self, element, text: str) -> bool:
        """Try LegacyIAccessiblePattern for older controls"""
        try:
            legacy_pattern = element.GetCurrentPattern(self.pattern_cache["legacy"])
            if legacy_pattern:
                legacy_pattern.SetValue(text + " ")
                return True
        except Exception:
            pass
        return False

    def _try_send_keys_fallback(self, element, text: str) -> bool:
        """Fallback to keyboard injection if patterns fail"""
        try:
            element.SetFocus()
            time.sleep(0.01)
            import keyboard

            keyboard.write(text + " ")
            return True
        except Exception:
            return False

    def is_available(self) -> bool:
        """Check if UI Automation is available"""
        return self.uia is not None


class EnhancedKeyboardStrategy(BaseInjectionStrategy):
    """Enhanced keyboard injection strategy with rate limiting"""

    def __init__(self):
        super().__init__(StrategyType.KEYBOARD.value)
        self.last_injection_time = 0

    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using keyboard library with rate limiting"""
        try:
            import keyboard

            keyboard.write(text + " ")
            return True
        except ImportError:
            return False

    def is_available(self) -> bool:
        """Check if keyboard library is available"""
        try:
            import keyboard

            return True
        except ImportError:
            return False


class EnhancedClipboardStrategy(BaseInjectionStrategy):
    """Enhanced clipboard strategy with format preservation"""

    def __init__(self):
        super().__init__(StrategyType.CLIPBOARD.value)
        self.clipboard_manager = None
        self._init_clipboard_manager()

    def _init_clipboard_manager(self):
        """Initialize clipboard manager"""
        try:
            import pyperclip

            self.clipboard_manager = pyperclip
            logger.info("Enhanced clipboard strategy initialized")
        except ImportError:
            self.clipboard_manager = None

    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using clipboard paste with format preservation"""
        if not self.clipboard_manager:
            return False

        try:
            # Save original clipboard
            original_content = self.clipboard_manager.paste()

            # Set new content
            self.clipboard_manager.copy(text + " ")

            # Perform paste
            import keyboard

            keyboard.send("ctrl+v")
            time.sleep(0.05)

            # Restore original content
            self.clipboard_manager.copy(original_content)

            return True

        except Exception as e:
            logger.debug(f"Clipboard injection failed: {e}")
            return False

    def is_available(self) -> bool:
        """Check if clipboard access is available"""
        return self.clipboard_manager is not None


class EnhancedWin32SendInputStrategy(BaseInjectionStrategy):
    """Enhanced Win32 SendInput strategy with Unicode support"""

    def __init__(self):
        super().__init__(StrategyType.WIN32_SENDINPUT.value)
        self.user32 = None
        self.input_struct = None
        self._init_win32()

    def _init_win32(self):
        """Initialize Win32 API access"""
        try:
            import ctypes
            from ctypes import Structure, Union, wintypes

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

            self.user32 = ctypes.windll.user32
            self.input_struct = INPUT
            self.INPUT_KEYBOARD = 1
            self.KEYEVENTF_UNICODE = 0x0004
            self.KEYEVENTF_KEYUP = 0x0002

            logger.info("Win32 SendInput strategy initialized")
        except Exception as e:
            logger.debug(f"Win32 initialization failed: {e}")
            self.user32 = None

    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using Win32 SendInput API"""
        if not self.user32:
            return False

        try:
            time.sleep(self.config["focus_delay"])

            for char in text + " ":
                if not self._send_unicode_char(char):
                    return False
                time.sleep(self.config["key_delay"])

            return True

        except Exception as e:
            logger.debug(f"Win32 SendInput injection failed: {e}")
            return False

    def _send_unicode_char(self, char: str) -> bool:
        """Send a single Unicode character"""
        try:
            import ctypes

            char_code = ord(char)
            ctypes.windll.user32.SendInput(
                1, ctypes.byref(ctypes.c_uint(char_code)), ctypes.sizeof(ctypes.c_uint)
            )
            return True
        except Exception:
            return False

    def is_available(self) -> bool:
        """Check if Win32 API is available"""
        return self.user32 is not None


class BasicKeyboardStrategy(BaseInjectionStrategy):
    """Basic keyboard strategy as ultimate fallback"""

    def __init__(self):
        super().__init__(StrategyType.BASIC_KEYBOARD.value)

    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Basic keyboard injection using keyboard library"""
        try:
            import keyboard

            keyboard.write(text + " ")
            return True
        except ImportError:
            return False

    def is_available(self) -> bool:
        """Check if basic keyboard is available"""
        try:
            import keyboard

            return True
        except ImportError:
            return False


class EnhancedInjectionManager:
    """Enhanced injection manager with strategy selection and performance tracking"""

    def __init__(self):
        self.strategies = {}
        self.strategy_stats = {}
        self.application_profiles = {}
        self._init_strategies()
        self._init_stats()

    def _init_strategies(self):
        """Initialize all available strategies"""
        strategy_classes = [
            EnhancedUIAutomationStrategy,
            EnhancedKeyboardStrategy,
            EnhancedClipboardStrategy,
            EnhancedWin32SendInputStrategy,
            BasicKeyboardStrategy,
        ]

        for strategy_class in strategy_classes:
            strategy = strategy_class()
            if strategy.is_available():
                self.strategies[strategy.name] = strategy
                logger.info(f"Strategy {strategy.name} initialized")

    def _init_stats(self):
        """Initialize strategy statistics"""
        for strategy_name in self.strategies:
            self.strategy_stats[strategy_name] = {
                "total_attempts": 0,
                "successful_injections": 0,
                "total_time": 0.0,
                "last_used": None,
            }

    def inject_text(self, text: str, app_info: Optional[ApplicationInfo] = None) -> InjectionResult:
        """Inject text using the best available strategy"""
        start_time = time.time()

        # Get strategy order based on application profile
        strategy_order = self._get_strategy_order(app_info)

        for strategy_name in strategy_order:
            if strategy_name not in self.strategies:
                continue

            strategy = self.strategies[strategy_name]
            result = self._try_inject_with_strategy(strategy, text, app_info)

            if result.success:
                self._update_stats(strategy_name, True, result.time_taken)
                return result
            else:
                self._update_stats(strategy_name, False, result.time_taken)

        # All strategies failed
        return InjectionResult(
            success=False,
            strategy_used="none",
            time_taken=time.time() - start_time,
            error_message="All injection strategies failed",
        )

    def _get_strategy_order(self, app_info: Optional[ApplicationInfo] = None) -> List[str]:
        """Get ordered list of strategies to try"""
        if app_info and app_info.profile:
            # Use application-specific strategy order
            return app_info.profile.injection_strategies

        # Default strategy order
        return [
            StrategyType.UI_AUTOMATION.value,
            StrategyType.KEYBOARD.value,
            StrategyType.CLIPBOARD.value,
            StrategyType.WIN32_SENDINPUT.value,
            StrategyType.BASIC_KEYBOARD.value,
        ]

    def _try_inject_with_strategy(
        self, strategy: BaseInjectionStrategy, text: str, app_info: Optional[ApplicationInfo] = None
    ) -> InjectionResult:
        """Try to inject text with a specific strategy"""
        start_time = time.time()

        try:
            success = strategy.inject(text, app_info)
            time_taken = time.time() - start_time

            return InjectionResult(
                success=success, strategy_used=strategy.name, time_taken=time_taken
            )

        except Exception as e:
            return InjectionResult(
                success=False,
                strategy_used=strategy.name,
                time_taken=time.time() - start_time,
                error_message=str(e),
            )

    def _update_stats(self, strategy_name: str, success: bool, time_taken: float):
        """Update strategy statistics"""
        if strategy_name in self.strategy_stats:
            stats = self.strategy_stats[strategy_name]
            stats["total_attempts"] += 1
            if success:
                stats["successful_injections"] += 1
            stats["total_time"] += time_taken
            stats["last_used"] = time.time()

    def get_strategy_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get current strategy statistics"""
        stats = {}
        for strategy_name, strategy_stats in self.strategy_stats.items():
            total = strategy_stats["total_attempts"]
            success = strategy_stats["successful_injections"]
            stats[strategy_name] = {
                "total_attempts": total,
                "successful_injections": success,
                "success_rate": (success / total * 100) if total > 0 else 0,
                "average_time": strategy_stats["total_time"] / total if total > 0 else 0,
                "last_used": strategy_stats["last_used"],
            }
        return stats

    def get_available_strategies(self) -> List[str]:
        """Get list of available strategies"""
        return list(self.strategies.keys())

    def update_strategy_config(self, strategy_name: str, config: Dict[str, Any]):
        """Update configuration for a specific strategy"""
        if strategy_name in self.strategies:
            self.strategies[strategy_name].update_config(config)

    def is_strategy_available(self, strategy_name: str) -> bool:
        """Check if a specific strategy is available"""
        return strategy_name in self.strategies


# Global instance
enhanced_injection_manager = EnhancedInjectionManager()
