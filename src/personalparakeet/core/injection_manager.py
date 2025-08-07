"""
Text Injection Manager for PersonalParakeet v3
Enhanced text injection with application-aware strategy selection
"""

import logging
import threading
import time
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from .application_detector import ApplicationInfo, ApplicationProfile, EnhancedApplicationDetector

logger = logging.getLogger(__name__)


class InjectionStrategy(Enum):
    """Available injection strategies"""

    KEYBOARD = auto()
    CLIPBOARD = auto()
    WIN32_SENDINPUT = auto()


class WindowsTextInjector:
    """Simplified Windows text injection with multiple strategies"""

    def __init__(self):
        self.strategies = {
            InjectionStrategy.KEYBOARD: self._inject_keyboard,
            InjectionStrategy.CLIPBOARD: self._inject_clipboard,
            InjectionStrategy.WIN32_SENDINPUT: self._inject_win32,
        }
        self.strategy_order = [
            InjectionStrategy.KEYBOARD,
            InjectionStrategy.CLIPBOARD,
            InjectionStrategy.WIN32_SENDINPUT,
        ]
        self.last_injection_time = 0
        self._init_dependencies()

    def _init_dependencies(self):
        """Initialize dependencies for each strategy"""
        # Check if keyboard library is available
        try:
            import keyboard

            self.has_keyboard = True
            logger.info("Keyboard injection strategy available")
        except ImportError:
            self.has_keyboard = False
            logger.warning("Keyboard library not available")

        # Check if Win32 API is available
        try:
            import ctypes
            from ctypes import wintypes

            self.user32 = ctypes.windll.user32
            self.has_win32 = True
            logger.info("Win32 SendInput strategy available")
        except Exception as e:
            self.has_win32 = False
            logger.warning(f"Win32 API not available: {e}")

        # Check if clipboard access is available
        try:
            import win32clipboard

            self.has_clipboard = True
            logger.info("Clipboard injection strategy available")
        except ImportError:
            # Try with pyperclip as fallback
            try:
                import pyperclip

                self.has_clipboard = True
                self.use_pyperclip = True
                logger.info("Clipboard injection strategy available (pyperclip)")
            except ImportError:
                self.has_clipboard = False
                self.use_pyperclip = False
                logger.warning("Clipboard access not available")

    def inject(self, text: str) -> bool:
        """
        Inject text using the first available strategy

        Args:
            text: Text to inject

        Returns:
            True if injection succeeded, False otherwise
        """
        if not text.strip():
            logger.warning("Empty text provided for injection")
            return False

        # Add space after text for natural dictation flow
        text_to_inject = text.strip() + " "

        # Rate limiting - prevent overwhelming the system
        current_time = time.time()
        if current_time - self.last_injection_time < 0.02:  # 20ms minimum between injections
            time.sleep(0.02)

        # Try strategies in order of preference
        for strategy in self.strategy_order:
            if self._is_strategy_available(strategy):
                try:
                    logger.debug(f"Attempting injection with {strategy.name}")
                    if self.strategies[strategy](text_to_inject):
                        self.last_injection_time = time.time()
                        logger.info(f"✓ Text injected successfully using {strategy.name}")
                        return True
                except Exception as e:
                    logger.debug(f"Strategy {strategy.name} failed: {e}")
                    continue

        logger.error("❌ All injection strategies failed")
        return False

    def _is_strategy_available(self, strategy: InjectionStrategy) -> bool:
        """Check if a specific strategy is available"""
        if strategy == InjectionStrategy.KEYBOARD:
            return self.has_keyboard
        elif strategy == InjectionStrategy.CLIPBOARD:
            return self.has_clipboard
        elif strategy == InjectionStrategy.WIN32_SENDINPUT:
            return self.has_win32
        return False

    def _inject_keyboard(self, text: str) -> bool:
        """Inject text using keyboard library"""
        if not self.has_keyboard:
            return False

        try:
            import keyboard

            # Small delay for focus acquisition
            time.sleep(0.01)

            # Type the text
            keyboard.write(text)
            logger.debug(f"Keyboard injection: '{text[:30]}...'")
            return True

        except Exception as e:
            logger.debug(f"Keyboard injection failed: {e}")
            return False

    def _inject_clipboard(self, text: str) -> bool:
        """Inject text using clipboard paste"""
        if not self.has_clipboard:
            return False

        try:
            # Save original clipboard content
            original_content = self._get_clipboard_content()

            # Set new clipboard content
            self._set_clipboard_content(text)

            # Simulate Ctrl+V
            self._send_paste_command()

            # Wait a bit for paste to complete
            time.sleep(0.05)

            # Restore original clipboard content
            if original_content is not None:
                self._set_clipboard_content(original_content)

            logger.debug(f"Clipboard injection: '{text[:30]}...'")
            return True

        except Exception as e:
            logger.debug(f"Clipboard injection failed: {e}")
            return False

    def _get_clipboard_content(self) -> Optional[str]:
        """Get current clipboard content"""
        try:
            if hasattr(self, "use_pyperclip") and self.use_pyperclip:
                import pyperclip

                return pyperclip.paste()
            else:
                import win32clipboard

                win32clipboard.OpenClipboard()
                try:
                    if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                        content = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                        return content
                finally:
                    win32clipboard.CloseClipboard()
        except Exception as e:
            logger.debug(f"Failed to get clipboard content: {e}")
        return None

    def _set_clipboard_content(self, text: str):
        """Set clipboard content"""
        if hasattr(self, "use_pyperclip") and self.use_pyperclip:
            import pyperclip

            pyperclip.copy(text)
        else:
            import win32clipboard

            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
            finally:
                win32clipboard.CloseClipboard()

    def _send_paste_command(self):
        """Send Ctrl+V command"""
        try:
            if self.has_keyboard:
                import keyboard

                keyboard.send("ctrl+v")
            elif self.has_win32:
                # Use Win32 API to send Ctrl+V
                self._send_key_combination([0x11, 0x56])  # Ctrl + V
            else:
                raise Exception("No method available to send paste command")
        except Exception as e:
            logger.debug(f"Failed to send paste command: {e}")
            raise

    def _inject_win32(self, text: str) -> bool:
        """Inject text using Win32 SendInput API"""
        if not self.has_win32:
            return False

        try:
            import ctypes
            from ctypes import wintypes

            # Focus acquisition delay
            time.sleep(0.01)

            # Send each Unicode character
            for char in text:
                self._send_unicode_char(ord(char))
                time.sleep(0.001)  # Small delay between characters

            logger.debug(f"Win32 injection: '{text[:30]}...'")
            return True

        except Exception as e:
            logger.debug(f"Win32 injection failed: {e}")
            return False

    def _send_unicode_char(self, char_code: int):
        """Send a single Unicode character using Win32 SendInput"""
        import ctypes
        from ctypes import Structure, Union, wintypes

        # Define INPUT structure
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

        # Constants
        INPUT_KEYBOARD = 1
        KEYEVENTF_UNICODE = 0x0004
        KEYEVENTF_KEYUP = 0x0002

        # Create key down event
        input_down = INPUT()
        input_down.type = INPUT_KEYBOARD
        input_down.union.ki.wVk = 0
        input_down.union.ki.wScan = char_code
        input_down.union.ki.dwFlags = KEYEVENTF_UNICODE
        input_down.union.ki.time = 0
        input_down.union.ki.dwExtraInfo = None

        # Create key up event
        input_up = INPUT()
        input_up.type = INPUT_KEYBOARD
        input_up.union.ki.wVk = 0
        input_up.union.ki.wScan = char_code
        input_up.union.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
        input_up.union.ki.time = 0
        input_up.union.ki.dwExtraInfo = None

        # Send key down and key up
        self.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(INPUT))
        self.user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(INPUT))

    def _send_key_combination(self, key_codes: List[int]):
        """Send a key combination using Win32 API"""
        try:
            # Press keys down
            for key_code in key_codes:
                self.user32.keybd_event(key_code, 0, 0, 0)
                time.sleep(0.001)

            # Release keys up (in reverse order)
            for key_code in reversed(key_codes):
                self.user32.keybd_event(key_code, 0, 2, 0)  # 2 = KEYEVENTF_KEYUP
                time.sleep(0.001)

        except Exception as e:
            logger.debug(f"Failed to send key combination: {e}")
            raise


class InjectionManager:
    """
    Enhanced injection manager for PersonalParakeet v3
    Handles text injection with application-aware strategy selection
    """

    def __init__(self):
        self.injector = WindowsTextInjector()
        self.app_detector = EnhancedApplicationDetector()
        self.injection_thread = None
        self.injection_lock = threading.Lock()
        self.injection_count = 0
        self.performance_stats = {
            "total_injections": 0,
            "successful_injections": 0,
            "strategy_usage": {},
            "app_type_stats": {},
        }

        logger.info("Enhanced InjectionManager initialized with application detection")

    def inject_text(self, text: str) -> bool:
        """
        Inject text into the active application with application-aware optimization

        Args:
            text: Text to inject

        Returns:
            True if injection succeeded, False otherwise
        """
        if not text or not text.strip():
            logger.warning("Attempted to inject empty text")
            return False

        # Use thread lock to prevent concurrent injections
        with self.injection_lock:
            try:
                self.injection_count += 1
                self.performance_stats["total_injections"] += 1

                # Detect current application
                app_info = self.app_detector.detect_current_application()
                if app_info:
                    logger.info(
                        f"Injecting text (#{self.injection_count}) into {app_info.name}: '{text.strip()[:50]}...'"
                    )

                    # Get optimized strategy order for this application
                    strategy_order = self.app_detector.get_optimized_strategy_order(app_info)
                    app_profile = self.app_detector.get_application_profile(app_info)

                    # Update injector strategy order
                    self._update_strategy_order(strategy_order)

                    # Apply application-specific timing
                    self._apply_application_profile(app_profile)

                    # Update stats
                    app_type_name = app_info.app_type.name
                    self.performance_stats["app_type_stats"][app_type_name] = (
                        self.performance_stats["app_type_stats"].get(app_type_name, 0) + 1
                    )
                else:
                    logger.info(
                        f"Injecting text (#{self.injection_count}) into unknown app: '{text.strip()[:50]}...'"
                    )

                # Perform injection (blocking call)
                success = self.injector.inject(text)

                if success:
                    self.performance_stats["successful_injections"] += 1
                    logger.info(f"✓ Text injection #{self.injection_count} completed successfully")
                else:
                    logger.error(f"❌ Text injection #{self.injection_count} failed")

                return success

            except Exception as e:
                logger.error(f"❌ Injection manager error: {e}")
                return False

    def inject_text_async(self, text: str) -> bool:
        """
        Inject text asynchronously (non-blocking)

        Args:
            text: Text to inject

        Returns:
            True if injection was queued successfully
        """
        try:
            # Start injection in a separate thread
            self.injection_thread = threading.Thread(
                target=self.inject_text, args=(text,), daemon=True
            )
            self.injection_thread.start()
            return True
        except Exception as e:
            logger.error(f"Failed to start async injection: {e}")
            return False

    def _update_strategy_order(self, strategy_names: List[str]):
        """Update injector strategy order based on application preferences"""
        # Map strategy names to enum values
        strategy_map = {
            "keyboard": InjectionStrategy.KEYBOARD,
            "clipboard": InjectionStrategy.CLIPBOARD,
            "win32_sendinput": InjectionStrategy.WIN32_SENDINPUT,
        }

        # Build new strategy order
        new_order = []
        for name in strategy_names:
            if name in strategy_map and self.injector._is_strategy_available(strategy_map[name]):
                new_order.append(strategy_map[name])

        # Ensure we have at least one strategy
        if not new_order:
            new_order = [
                s for s in self.injector.strategy_order if self.injector._is_strategy_available(s)
            ]

        if new_order:
            self.injector.strategy_order = new_order
            logger.debug(f"Updated strategy order: {[s.name for s in new_order]}")

    def _apply_application_profile(self, profile: ApplicationProfile):
        """Apply application-specific timing and behavior settings"""
        # Currently the WindowsTextInjector doesn't have configurable timing,
        # but we can log the profile information for future enhancement
        logger.debug(
            f"Applying profile for {profile.name}: "
            f"key_delay={profile.key_delay}, "
            f"focus_delay={profile.focus_delay}, "
            f"requires_slow_typing={profile.requires_slow_typing}"
        )

        # TODO: In future enhancement, modify injector timing based on profile
        # For now, this provides the framework for application-specific behavior

    def get_current_application(self) -> Optional[ApplicationInfo]:
        """Get information about the currently active application"""
        try:
            return self.app_detector.detect_current_application()
        except Exception as e:
            logger.error(f"Failed to detect current application: {e}")
            return None

    def get_application_profile(
        self, app_info: Optional[ApplicationInfo] = None
    ) -> ApplicationProfile:
        """Get the injection profile for the specified or current application"""
        if not app_info:
            app_info = self.get_current_application()

        if app_info:
            return self.app_detector.get_application_profile(app_info)
        else:
            return self.app_detector._get_default_profile()

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        success_rate = 0.0
        if self.performance_stats["total_injections"] > 0:
            success_rate = (
                self.performance_stats["successful_injections"]
                / self.performance_stats["total_injections"]
            ) * 100

        return {
            "total_injections": self.performance_stats["total_injections"],
            "successful_injections": self.performance_stats["successful_injections"],
            "success_rate_percent": round(success_rate, 1),
            "app_type_distribution": self.performance_stats["app_type_stats"].copy(),
            "detector_status": self.app_detector.get_detector_status(),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive injection manager status"""
        current_app = self.get_current_application()

        status = {
            "injection_count": self.injection_count,
            "has_keyboard": self.injector.has_keyboard,
            "has_clipboard": self.injector.has_clipboard,
            "has_win32": self.injector.has_win32,
            "available_strategies": [
                strategy.name
                for strategy in self.injector.strategy_order
                if self.injector._is_strategy_available(strategy)
            ],
            "current_application": {
                "name": current_app.name if current_app else "Unknown",
                "type": current_app.app_type.name if current_app else "UNKNOWN",
                "window_title": current_app.window_title if current_app else "",
            },
            "performance_stats": self.get_performance_stats(),
        }

        return status
