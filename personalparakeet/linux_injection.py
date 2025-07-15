"""Linux-specific text injection strategies

Implements injection methods for:
- X11 sessions (KDE, GNOME, generic)
- Wayland sessions (with fallbacks)
- Terminal emulators
- Linux-specific applications
"""

import os
import time
import subprocess
from typing import Optional
from .text_injection import TextInjectionStrategy, ApplicationInfo, ApplicationType
from .logger import setup_logger

logger = setup_logger(__name__)


class LinuxXTestStrategy(TextInjectionStrategy):
    """X11 XTEST injection - most reliable for KDE and X11 sessions
    
    Based on the design.md KDEPlasmaInjector implementation.
    """
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.display = None
        self.xtest = None
        self.X = None
        self._init_x11()
    
    def _init_x11(self):
        """Initialize X11 and XTEST extension"""
        try:
            from Xlib import display, X
            from Xlib.ext import xtest
            self.display = display.Display()
            self.xtest = xtest
            self.X = X
            logger.info("X11 XTEST initialized successfully")
        except ImportError:
            logger.warning("python-xlib not installed, XTEST injection unavailable")
        except Exception as e:
            logger.warning(f"Failed to initialize X11: {e}")
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using XTEST extension"""
        if not self.display:
            return False
        
        try:
            # Add small delay to ensure focus
            time.sleep(self.config.focus_acquisition_delay)
            
            # Special handling for specific applications
            if app_info and app_info.window_class:
                window_class = app_info.window_class.lower()
                
                # Konsole optimization - use D-Bus if available
                if window_class == 'konsole':
                    if self._inject_konsole_dbus(text):
                        return True
            
            # Default XTEST injection
            for char in text + " ":
                try:
                    keycode = self.display.keysym_to_keycode(ord(char))
                    if keycode:
                        self.xtest.fake_input(self.display, self.X.KeyPress, keycode)
                        self.xtest.fake_input(self.display, self.X.KeyRelease, keycode)
                except Exception as e:
                    logger.warning(f"Failed to inject character '{char}': {e}")
            
            self.display.sync()
            return True
            
        except Exception as e:
            logger.error(f"XTEST injection failed: {e}")
            return False
    
    def _inject_konsole_dbus(self, text: str) -> bool:
        """Try D-Bus injection for Konsole (KDE terminal)"""
        try:
            subprocess.run([
                'qdbus', 'org.kde.konsole', '/konsole/MainWindow_1',
                'org.kde.konsole.Window.sendText', text
            ], check=True, capture_output=True)
            return True
        except:
            return False
    
    def is_available(self) -> bool:
        """Check if XTEST is available"""
        return self.display is not None


class LinuxXdotoolStrategy(TextInjectionStrategy):
    """Xdotool-based injection - widely compatible fallback"""
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.xdotool_available = self._check_xdotool()
    
    def _check_xdotool(self) -> bool:
        """Check if xdotool is installed"""
        try:
            subprocess.run(['xdotool', '--version'], 
                         capture_output=True, check=True)
            logger.info("xdotool is available")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("xdotool not installed")
            return False
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using xdotool"""
        if not self.xdotool_available:
            return False
        
        try:
            # Add small delay to ensure focus
            time.sleep(self.config.focus_acquisition_delay)
            
            # Use xdotool type command with --clearmodifiers for reliability
            # This handles shift states and special characters automatically
            subprocess.run([
                'xdotool', 'type', '--clearmodifiers', '--delay', '10', 
                text + " "
            ], check=True, timeout=self.config.xdotool_timeout)
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("xdotool timed out")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"xdotool failed: {e}")
            return False
        except Exception as e:
            logger.error(f"xdotool injection error: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if xdotool is available"""
        return self.xdotool_available


class LinuxATSPIStrategy(TextInjectionStrategy):
    """AT-SPI accessibility framework injection - Wayland compatible
    
    Based on the design.md GNOMEInjector implementation.
    """
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.at_spi = None
        self._init_at_spi()
    
    def _init_at_spi(self):
        """Initialize AT-SPI accessibility framework"""
        try:
            import pyatspi
            self.at_spi = pyatspi
            logger.info("AT-SPI initialized successfully")
        except ImportError:
            logger.warning("pyatspi not installed, AT-SPI injection unavailable")
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using AT-SPI"""
        if not self.at_spi:
            # Try fallback to wtype for Wayland
            return self._inject_wtype(text)
        
        try:
            # Get focused object via AT-SPI
            registry = self.at_spi.Registry()
            desktop = registry.getDesktop(0)
            
            # Find focused text object
            focused = self._find_focused_text_object(desktop)
            if focused:
                # Insert text at current position
                current_text = focused.get_text_contents() or ""
                focused.set_text_contents(current_text + text + " ")
                return True
            
            # No focused text object found
            return False
            
        except Exception as e:
            logger.error(f"AT-SPI injection failed: {e}")
            # Try wtype as fallback
            return self._inject_wtype(text)
    
    def _find_focused_text_object(self, obj):
        """Recursively find the focused text-editable object"""
        try:
            if obj.getState().contains(self.at_spi.STATE_FOCUSED):
                if obj.getRole() in [self.at_spi.ROLE_TEXT, 
                                   self.at_spi.ROLE_ENTRY,
                                   self.at_spi.ROLE_TERMINAL]:
                    return obj
            
            # Search children
            for i in range(obj.childCount):
                child = obj.getChildAtIndex(i)
                result = self._find_focused_text_object(child)
                if result:
                    return result
        except:
            pass
        return None
    
    def _inject_wtype(self, text: str) -> bool:
        """Fallback to wtype for Wayland"""
        try:
            subprocess.run(['wtype', text + " "], check=True, timeout=self.config.kde_dbus_timeout)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
        except subprocess.TimeoutExpired:
            logger.error("wtype timed out")
            return False
    
    def is_available(self) -> bool:
        """Check if AT-SPI or wtype is available"""
        if self.at_spi:
            return True
        
        # Check for wtype as fallback
        try:
            subprocess.run(['wtype', '--version'], 
                         capture_output=True, check=True)
            return True
        except:
            return False


from .linux_clipboard_manager import LinuxClipboardManager


class LinuxClipboardStrategy(TextInjectionStrategy):
    """Clipboard-based injection for Linux"""
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.clipboard_manager = LinuxClipboardManager(self.config.max_clipboard_retries, self.config.clipboard_retry_delay)
        self.display = None
        self._init_x11_for_paste()
    
    def _init_x11_for_paste(self):
        """Initialize X11 for sending Ctrl+V"""
        try:
            from Xlib import display, X, XK
            from Xlib.ext import xtest
            self.display = display.Display()
            self.xtest = xtest
            self.X = X
            self.XK = XK
        except:
            pass
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text via clipboard"""
        if not self.clipboard_manager.is_available():
            return False
        
        try:
            # Save current clipboard content
            self.clipboard_manager.save_clipboard()
            
            # Set new clipboard content
            self.clipboard_manager._set_clipboard_content(text + " ")
            
            # Small delay to ensure clipboard is set
            time.sleep(self.config.clipboard_paste_delay)
            
            # Trigger paste
            if self._trigger_paste():
                # Restore original clipboard after a delay
                time.sleep(self.config.clipboard_paste_delay)
                self.clipboard_manager.restore_clipboard()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Clipboard injection failed: {e}")
            return False
    
    def _trigger_paste(self) -> bool:
        """Trigger Ctrl+V paste"""
        # Try X11 method first
        if self.display and self.xtest:
            try:
                ctrl = self.display.keysym_to_keycode(self.XK.XK_Control_L)
                v = self.display.keysym_to_keycode(ord('v'))
                
                self.xtest.fake_input(self.display, self.X.KeyPress, ctrl)
                self.xtest.fake_input(self.display, self.X.KeyPress, v)
                self.xtest.fake_input(self.display, self.X.KeyRelease, v)
                self.xtest.fake_input(self.display, self.X.KeyRelease, ctrl)
                self.display.sync()
                return True
            except:
                pass
        
        # Fallback to xdotool
        try:
            subprocess.run(['xdotool', 'key', 'ctrl+v'], check=True)
            return True
        except:
            pass
        
        # Last resort: keyboard library
        try:
            import keyboard
            keyboard.press_and_release('ctrl+v')
            return True
        except:
            return False
    
    def is_available(self) -> bool:
        """Check if clipboard injection is available"""
        return self.clipboard_manager.is_available()