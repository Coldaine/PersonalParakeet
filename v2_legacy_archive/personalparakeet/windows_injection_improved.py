"""Improved Windows-specific text injection strategies

This module contains enhanced versions of Windows injection strategies with:
- Better error handling and debugging
- Improved reliability and compatibility
- Enhanced application-specific optimizations
- Retry mechanisms for transient failures
"""

import time
import keyboard
import threading
from typing import Optional, Dict, Any, Callable
from .text_injection import TextInjectionStrategy, ApplicationInfo, ApplicationType
from .config import InjectionConfig
from .logger import setup_logger
from .constants import LogEmoji

logger = setup_logger(__name__)


class ImprovedWindowsUIAutomationStrategy(TextInjectionStrategy):
    """Enhanced Windows UI Automation API strategy
    
    Improvements:
    - Better error handling with specific error types
    - Fallback patterns for different control types
    - Retry mechanisms for transient failures
    - Enhanced debugging information
    """
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.uia = None
        self.pattern_cache: Dict[str, Any] = {}
        self._init_ui_automation()
    
    def _init_ui_automation(self):
        """Initialize Windows UI Automation COM objects with better error handling"""
        try:
            import comtypes.client
            from comtypes import automation
            
            # Create UI Automation instance
            self.uia = comtypes.client.CreateObject(
                "{ff48dba4-60ef-4201-aa87-54103eef594e}",
                interface=automation.IUIAutomation
            )
            
            # Cache common pattern IDs
            self.pattern_cache = {
                'text': 10014,      # UIA_TextPatternId
                'value': 10002,     # UIA_ValuePatternId
                'legacy': 10018,    # UIA_LegacyIAccessiblePatternId
                'invoke': 10000,    # UIA_InvokePatternId
                'selection': 10001, # UIA_SelectionPatternId
            }
            
            logger.info(f"{LogEmoji.SUCCESS} Windows UI Automation initialized successfully")
        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Failed to initialize UI Automation: {e}")
            self.uia = None
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using enhanced UI Automation with fallback patterns"""
        if not self.uia:
            logger.warning(f"{LogEmoji.WARNING} UI Automation not available")
            return False
        
        # Add debugging information
        logger.debug(f"{LogEmoji.INFO} Attempting UI Automation injection: '{text[:20]}...'")
        
        try:
            # Get the currently focused element with retry
            focused = self._get_focused_element_with_retry()
            if not focused:
                logger.warning(f"{LogEmoji.WARNING} No focused element found")
                return False
            
            # Log element information for debugging
            self._log_element_info(focused)
            
            # Try different injection patterns in order of reliability
            patterns_to_try = [
                ('text', self._try_text_pattern),
                ('value', self._try_value_pattern),
                ('legacy', self._try_legacy_pattern),
                ('send_keys', self._try_send_keys_fallback)
            ]
            
            for pattern_name, pattern_func in patterns_to_try:
                try:
                    logger.debug(f"{LogEmoji.INFO} Trying {pattern_name} pattern...")
                    if pattern_func(focused, text):
                        logger.info(f"{LogEmoji.SUCCESS} UI Automation injection successful with {pattern_name}")
                        return True
                except Exception as e:
                    logger.debug(f"{LogEmoji.WARNING} {pattern_name} pattern failed: {e}")
                    continue
            
            logger.warning(f"{LogEmoji.WARNING} All UI Automation patterns failed")
            return False
            
        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} UI Automation injection failed: {e}")
            return False
    
    def _get_focused_element_with_retry(self, max_retries: int = 3):
        """Get focused element with retry mechanism"""
        for attempt in range(max_retries):
            try:
                focused = self.uia.GetFocusedElement()
                if focused:
                    return focused
                time.sleep(0.01)  # Small delay between retries
            except Exception as e:
                logger.debug(f"Focused element attempt {attempt + 1} failed: {e}")
                time.sleep(0.01)
        return None
    
    def _log_element_info(self, element):
        """Log element information for debugging"""
        try:
            control_type = element.CurrentControlType
            name = element.CurrentName or "Unknown"
            class_name = element.CurrentClassName or "Unknown"
            logger.debug(f"{LogEmoji.INFO} Focused element: {name} (type: {control_type}, class: {class_name})")
        except Exception as e:
            logger.debug(f"Could not get element info: {e}")
    
    def _try_text_pattern(self, element, text: str) -> bool:
        """Try TextPattern for rich text controls"""
        try:
            text_pattern = element.GetCurrentPattern(self.pattern_cache['text'])
            if text_pattern:
                # Get document range and insert text
                doc_range = text_pattern.DocumentRange
                if doc_range:
                    # Try to get selection first
                    try:
                        selection = text_pattern.GetSelection()
                        if selection and len(selection) > 0:
                            # Insert at selection
                            selection[0].InsertText(text + " ")
                        else:
                            # Insert at end
                            doc_range.InsertText(text + " ")
                        return True
                    except:
                        # Fallback to document range
                        doc_range.InsertText(text + " ")
                        return True
        except Exception as e:
            logger.debug(f"TextPattern failed: {e}")
        return False
    
    def _try_value_pattern(self, element, text: str) -> bool:
        """Try ValuePattern for simple text inputs"""
        try:
            value_pattern = element.GetCurrentPattern(self.pattern_cache['value'])
            if value_pattern:
                # Check if element is read-only
                if hasattr(value_pattern, 'CurrentIsReadOnly') and value_pattern.CurrentIsReadOnly:
                    logger.debug("Element is read-only, skipping ValuePattern")
                    return False
                
                # Get current value and append
                current = value_pattern.CurrentValue or ""
                new_value = current + text + " "
                value_pattern.SetValue(new_value)
                return True
        except Exception as e:
            logger.debug(f"ValuePattern failed: {e}")
        return False
    
    def _try_legacy_pattern(self, element, text: str) -> bool:
        """Try LegacyIAccessiblePattern for older controls"""
        try:
            legacy_pattern = element.GetCurrentPattern(self.pattern_cache['legacy'])
            if legacy_pattern:
                # Try to set value through legacy interface
                legacy_pattern.SetValue(text + " ")
                return True
        except Exception as e:
            logger.debug(f"LegacyPattern failed: {e}")
        return False
    
    def _try_send_keys_fallback(self, element, text: str) -> bool:
        """Fallback using SendKeys if patterns fail"""
        try:
            # Focus the element first
            element.SetFocus()
            time.sleep(0.01)
            
            # Use keyboard library as fallback
            keyboard.write(text + " ")
            return True
        except Exception as e:
            logger.debug(f"SendKeys fallback failed: {e}")
        return False
    
    def is_available(self) -> bool:
        """Check if UI Automation is available"""
        return self.uia is not None


class ImprovedWindowsKeyboardStrategy(TextInjectionStrategy):
    """Enhanced keyboard injection strategy with better reliability"""
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.last_injection_time = 0
        self.injection_count = 0
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using enhanced keyboard method"""
        try:
            # Rate limiting to prevent overwhelming the system
            current_time = time.time()
            if current_time - self.last_injection_time < 0.01:  # 10ms minimum between injections
                time.sleep(0.01)
            
            # Ensure proper focus acquisition
            time.sleep(self.config.focus_acquisition_delay)
            
            # Try different keyboard injection methods
            methods = [
                self._try_keyboard_write,
                self._try_keyboard_type,
                self._try_char_by_char
            ]
            
            for method in methods:
                try:
                    if method(text):
                        self.last_injection_time = time.time()
                        self.injection_count += 1
                        logger.info(f"{LogEmoji.SUCCESS} Keyboard injection successful (count: {self.injection_count})")
                        return True
                except Exception as e:
                    logger.debug(f"Keyboard method failed: {e}")
                    continue
            
            logger.warning(f"{LogEmoji.WARNING} All keyboard methods failed")
            return False
            
        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Keyboard injection failed: {e}")
            return False
    
    def _try_keyboard_write(self, text: str) -> bool:
        """Try standard keyboard.write method"""
        keyboard.write(text + " ")
        return True
    
    def _try_keyboard_type(self, text: str) -> bool:
        """Try keyboard.type method (alias for write)"""
        keyboard.type(text + " ")
        return True
    
    def _try_char_by_char(self, text: str) -> bool:
        """Try character-by-character injection with delays"""
        for char in text + " ":
            keyboard.write(char)
            time.sleep(self.config.default_key_delay)
        return True
    
    def is_available(self) -> bool:
        """Check if keyboard library is available"""
        try:
            return hasattr(keyboard, 'write') and hasattr(keyboard, 'is_pressed')
        except Exception:
            return False


class ImprovedWindowsClipboardStrategy(TextInjectionStrategy):
    """Enhanced clipboard strategy with better error handling"""
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.clipboard_manager = None
        self._init_clipboard_manager()
    
    def _init_clipboard_manager(self):
        """Initialize clipboard manager with error handling"""
        try:
            from .windows_clipboard_manager import WindowsClipboardManager
            self.clipboard_manager = WindowsClipboardManager()
            logger.info(f"{LogEmoji.SUCCESS} Windows clipboard manager initialized")
        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Failed to initialize clipboard manager: {e}")
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text via enhanced clipboard paste"""
        if not self.clipboard_manager or not self.clipboard_manager.is_available():
            logger.warning(f"{LogEmoji.WARNING} Clipboard not available")
            return False
        
        try:
            # Save current clipboard with retry
            original_content = self._save_clipboard_with_retry()
            
            # Set clipboard content
            if not self._set_clipboard_content(text + " "):
                logger.warning(f"{LogEmoji.WARNING} Failed to set clipboard content")
                return False
            
            # Perform paste operation
            success = self._paste_with_retry()
            
            # Restore original clipboard content
            self._restore_clipboard_with_retry(original_content)
            
            if success:
                logger.info(f"{LogEmoji.SUCCESS} Clipboard injection successful")
            else:
                logger.warning(f"{LogEmoji.WARNING} Clipboard paste failed")
            
            return success
            
        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Clipboard injection failed: {e}")
            return False
    
    def _save_clipboard_with_retry(self, max_retries: int = 3) -> str:
        """Save clipboard content with retry mechanism"""
        for attempt in range(max_retries):
            try:
                content = self.clipboard_manager.save_clipboard()
                if content is not None:
                    return content
                time.sleep(0.01)
            except Exception as e:
                logger.debug(f"Clipboard save attempt {attempt + 1} failed: {e}")
                time.sleep(0.01)
        return ""
    
    def _set_clipboard_content(self, text: str) -> bool:
        """Set clipboard content with validation"""
        try:
            self.clipboard_manager._set_clipboard_content(text)
            # Verify content was set
            time.sleep(0.01)
            return True
        except Exception as e:
            logger.debug(f"Set clipboard content failed: {e}")
            return False
    
    def _paste_with_retry(self, max_retries: int = 3) -> bool:
        """Perform paste operation with retry"""
        for attempt in range(max_retries):
            try:
                # Try different paste methods
                paste_methods = [
                    lambda: keyboard.send('ctrl+v'),
                    lambda: keyboard.press_and_release('ctrl+v'),
                    lambda: self._manual_paste()
                ]
                
                for method in paste_methods:
                    try:
                        method()
                        time.sleep(self.config.clipboard_paste_delay)
                        return True
                    except Exception as e:
                        logger.debug(f"Paste method failed: {e}")
                        continue
                
                time.sleep(0.01)
            except Exception as e:
                logger.debug(f"Paste attempt {attempt + 1} failed: {e}")
                time.sleep(0.01)
        return False
    
    def _manual_paste(self):
        """Manual paste using individual key presses"""
        keyboard.press('ctrl')
        keyboard.press('v')
        keyboard.release('v')
        keyboard.release('ctrl')
    
    def _restore_clipboard_with_retry(self, content: str, max_retries: int = 3):
        """Restore clipboard content with retry"""
        for attempt in range(max_retries):
            try:
                self.clipboard_manager.restore_clipboard(content)
                return
            except Exception as e:
                logger.debug(f"Clipboard restore attempt {attempt + 1} failed: {e}")
                time.sleep(0.01)
    
    def is_available(self) -> bool:
        """Check if clipboard access is available"""
        return self.clipboard_manager and self.clipboard_manager.is_available()


class ImprovedWindowsSendInputStrategy(TextInjectionStrategy):
    """Enhanced Win32 SendInput strategy with better Unicode support"""
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.user32 = None
        self.input_struct = None
        self._init_win32_enhanced()
    
    def _init_win32_enhanced(self):
        """Initialize enhanced Win32 API access"""
        try:
            import ctypes
            from ctypes import wintypes, Structure, Union, c_ulong, c_ushort, c_short, POINTER
            
            # Define enhanced INPUT structure
            class KEYBDINPUT(Structure):
                _fields_ = [
                    ("wVk", wintypes.WORD),
                    ("wScan", wintypes.WORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", POINTER(wintypes.ULONG))
                ]
            
            class MOUSEINPUT(Structure):
                _fields_ = [
                    ("dx", wintypes.LONG),
                    ("dy", wintypes.LONG),
                    ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", POINTER(wintypes.ULONG))
                ]
            
            class HARDWAREINPUT(Structure):
                _fields_ = [
                    ("uMsg", wintypes.DWORD),
                    ("wParamL", wintypes.WORD),
                    ("wParamH", wintypes.WORD)
                ]
            
            class DUMMYUNIONNAME(Union):
                _fields_ = [
                    ("mi", MOUSEINPUT),
                    ("ki", KEYBDINPUT),
                    ("hi", HARDWAREINPUT)
                ]
            
            class INPUT(Structure):
                _fields_ = [
                    ("type", wintypes.DWORD),
                    ("dummyunionname", DUMMYUNIONNAME)
                ]
            
            self.user32 = ctypes.windll.user32
            self.input_struct = INPUT
            
            # Constants
            self.INPUT_KEYBOARD = 1
            self.KEYEVENTF_UNICODE = 0x0004
            self.KEYEVENTF_KEYUP = 0x0002
            
            logger.info(f"{LogEmoji.SUCCESS} Enhanced Win32 SendInput initialized")
        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} Failed to initialize enhanced Win32 API: {e}")
            self.user32 = None
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using enhanced Win32 SendInput"""
        if not self.user32:
            logger.warning(f"{LogEmoji.WARNING} Win32 SendInput not available")
            return False
        
        try:
            # Focus acquisition delay
            time.sleep(self.config.focus_acquisition_delay)
            
            # Send each character with proper Unicode handling
            for char in text + " ":
                if not self._send_unicode_char(char):
                    logger.warning(f"{LogEmoji.WARNING} Failed to send character: {char}")
                    # Continue with other characters
                time.sleep(self.config.default_key_delay)
            
            logger.info(f"{LogEmoji.SUCCESS} SendInput injection successful")
            return True
            
        except Exception as e:
            logger.error(f"{LogEmoji.ERROR} SendInput injection failed: {e}")
            return False
    
    def _send_unicode_char(self, char: str) -> bool:
        """Send a single Unicode character using SendInput"""
        try:
            import ctypes
            
            # Create INPUT structure for key down
            input_down = self.input_struct()
            input_down.type = self.INPUT_KEYBOARD
            input_down.dummyunionname.ki.wVk = 0
            input_down.dummyunionname.ki.wScan = ord(char)
            input_down.dummyunionname.ki.dwFlags = self.KEYEVENTF_UNICODE
            input_down.dummyunionname.ki.time = 0
            input_down.dummyunionname.ki.dwExtraInfo = None
            
            # Create INPUT structure for key up
            input_up = self.input_struct()
            input_up.type = self.INPUT_KEYBOARD
            input_up.dummyunionname.ki.wVk = 0
            input_up.dummyunionname.ki.wScan = ord(char)
            input_up.dummyunionname.ki.dwFlags = self.KEYEVENTF_UNICODE | self.KEYEVENTF_KEYUP
            input_up.dummyunionname.ki.time = 0
            input_up.dummyunionname.ki.dwExtraInfo = None
            
            # Send key down
            result1 = self.user32.SendInput(1, ctypes.byref(input_down), ctypes.sizeof(input_down))
            # Send key up
            result2 = self.user32.SendInput(1, ctypes.byref(input_up), ctypes.sizeof(input_up))
            
            return result1 == 1 and result2 == 1
            
        except Exception as e:
            logger.debug(f"Failed to send Unicode char '{char}': {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if enhanced Win32 API is available"""
        return self.user32 is not None and self.input_struct is not None


# Strategy registry for easy access
IMPROVED_WINDOWS_STRATEGIES = {
    'ui_automation': ImprovedWindowsUIAutomationStrategy,
    'keyboard': ImprovedWindowsKeyboardStrategy,
    'clipboard': ImprovedWindowsClipboardStrategy,
    'send_input': ImprovedWindowsSendInputStrategy,
}