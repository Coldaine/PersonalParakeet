"""Windows-specific text injection strategies

Implements multiple injection methods for Windows including:
- UI Automation API (most reliable, similar to Win+H)
- Direct keyboard injection
- Clipboard paste
- Win32 SendInput
"""

import time
import keyboard
from typing import Optional
from .text_injection import TextInjectionStrategy, ApplicationInfo, ApplicationType
from .config import InjectionConfig
from .logger import setup_logger

logger = setup_logger(__name__)


class WindowsUIAutomationStrategy(TextInjectionStrategy):
    """Windows UI Automation API for smart text injection
    
    This is the most reliable method, similar to how Windows Speech Recognition
    (Win+H) injects text. It works with most modern Windows applications.
    """
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.uia = None
        self._init_ui_automation()
    
    def _init_ui_automation(self):
        """Initialize Windows UI Automation COM objects"""
        try:
            import comtypes.client
            from comtypes import automation
            
            # Create UI Automation instance
            # CLSID for IUIAutomation interface
            self.uia = comtypes.client.CreateObject(
                "{ff48dba4-60ef-4201-aa87-54103eef594e}",
                interface=automation.IUIAutomation
            )
            logger.info("Windows UI Automation initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize UI Automation: {e}")
            self.uia = None
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using UI Automation API"""
        if not self.uia:
            return False
        
        try:
            # Get the currently focused element
            focused = self.uia.GetFocusedElement()
            if not focused:
                logger.warning("No focused element found")
                return False
            
            # Pattern IDs from UI Automation
            UIA_TextPatternId = 10014
            UIA_ValuePatternId = 10002
            
            # First try TextPattern (for rich text controls like Word, VS Code)
            try:
                text_pattern = focused.GetCurrentPattern(UIA_TextPatternId)
                if text_pattern:
                    # Insert text at current position
                    text_pattern.DocumentRange.InsertText(text + " ")
                    return True
            except Exception as e:
                # TextPattern not supported, try ValuePattern
                pass
            
            # Try ValuePattern (for simple text inputs like browsers, notepad)
            try:
                value_pattern = focused.GetCurrentPattern(UIA_ValuePatternId)
                if value_pattern:
                    # Get current value and append
                    current = value_pattern.CurrentValue or ""
                    value_pattern.SetValue(current + text + " ")
                    return True
            except Exception as e:
                logger.warning(f"ValuePattern failed: {e}")
            
            # Neither pattern worked
            return False
            
        except Exception as e:
            logger.error(f"UI Automation injection failed: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if UI Automation is available"""
        return self.uia is not None


class WindowsKeyboardStrategy(TextInjectionStrategy):
    """Direct keyboard injection for Windows"""
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using keyboard.write()"""
        try:
            # Small delay to ensure focus
            time.sleep(self.config.focus_acquisition_delay)
            
            # Use keyboard.write for direct injection
            keyboard.write(text + " ")
            return True
            
        except Exception as e:
            logger.error(f"Windows keyboard injection failed: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if keyboard library is available"""
        try:
            _ = keyboard.is_pressed
            return True
        except Exception:
            return False


from .windows_clipboard_manager import WindowsClipboardManager


class WindowsClipboardStrategy(TextInjectionStrategy):
    """Clipboard-based injection for Windows
    
    Best for code editors and applications that support paste operations.
    """
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.clipboard_manager = WindowsClipboardManager()
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text via clipboard paste"""
        if not self.clipboard_manager.is_available():
            return False
        
        try:
            # Save current clipboard content
            self.clipboard_manager.save_clipboard()
            
            # Set new clipboard content
            self.clipboard_manager._set_clipboard_content(text + " ")
            
            # Paste using Ctrl+V
            keyboard.press_and_release('ctrl+v')
            
            # Small delay to ensure paste completes
            time.sleep(self.config.clipboard_paste_delay)
            
            # Restore original clipboard content
            self.clipboard_manager.restore_clipboard()
            
            return True
            
        except Exception as e:
            logger.error(f"Windows clipboard injection failed: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if clipboard access is available"""
        return self.clipboard_manager.is_available()


class WindowsSendInputStrategy(TextInjectionStrategy):
    """Low-level Win32 SendInput API for complex scenarios
    
    This is a more direct method that can work in situations where
    other methods fail, but it requires more setup.
    """
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.ctypes = None
        self.user32 = None
        self._init_win32()
    
    def _init_win32(self):
        """Initialize Win32 API access"""
        try:
            import ctypes
            from ctypes import wintypes
            
            self.ctypes = ctypes
            self.user32 = ctypes.windll.user32
            
            # Define necessary structures
            self.KEYEVENTF_UNICODE = 0x0004
            self.KEYEVENTF_KEYUP = 0x0002
            
            logger.info("Win32 SendInput initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Win32 API: {e}")
            self.user32 = None
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using Win32 SendInput"""
        if not self.user32:
            return False
        
        try:
            # Small delay to ensure focus
            time.sleep(self.config.focus_acquisition_delay)
            
            # Send each character as Unicode input
            for char in text + " ":
                # Key down
                self.user32.keybd_event(0, ord(char), self.KEYEVENTF_UNICODE, 0)
                # Key up
                self.user32.keybd_event(0, ord(char), 
                                      self.KEYEVENTF_UNICODE | self.KEYEVENTF_KEYUP, 0)
                # Small delay between characters
                time.sleep(self.config.default_key_delay)
            
            return True
            
        except Exception as e:
            logger.error(f"Win32 SendInput failed: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if Win32 API is available"""
        return self.user32 is not None