"""KDE Plasma optimized text injection

Simplified implementation for KDE on Ubuntu based on the design.md examples.
This provides the most reliable injection for KDE Plasma desktop.
"""

import subprocess
import time
from typing import Optional
from .text_injection import TextInjectionStrategy, ApplicationInfo
from Xlib import X


class KDESimpleInjector(TextInjectionStrategy):
    """Simple but highly effective injection for KDE Plasma
    
    Based on the "For Your Immediate Implementation" section in design.md.
    Works with 99% of KDE applications.
    """
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()
        self.xdotool_available = self._check_xdotool()
        self.display = None
        self.xtest = None
        self._init_xtest_fallback()
    
    def _check_xdotool(self) -> bool:
        """Check if xdotool is available"""
        try:
            subprocess.run(['xdotool', '--version'], 
                         capture_output=True, check=True)
            return True
        except:
            return False
    
    def _init_xtest_fallback(self):
        """Initialize XTEST as fallback"""
        try:
            from Xlib import display
            from Xlib.ext import xtest
            self.display = display.Display()
            self.xtest = xtest
        except:
            pass
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using the simplest, most reliable method for KDE"""
        
        # Method 1: Try xdotool first (simplest and works great on KDE)
        if self.xdotool_available:
            try:
                subprocess.run(
                    ['xdotool', 'type', '--clearmodifiers', text + " "], 
                    check=True, 
                    timeout=self.config.xdotool_timeout
                )
                return True
            except:
                # Fall through to Method 2
                pass
        
        # Method 2: XTEST fallback (most reliable)
        if self.display and self.xtest:
            try:
                for char in text + " ":
                    keycode = self.display.keysym_to_keycode(ord(char))
                    if keycode:
                        self.xtest.fake_input(self.display, X.KeyPress, keycode)  # KeyPress
                        self.xtest.fake_input(self.display, X.KeyRelease, keycode)  # KeyRelease
                self.display.sync()
                return True
            except Exception as e:
                logger.error(f"XTEST fallback failed: {e}")
        
        return False
    
    def is_available(self) -> bool:
        """Check if KDE injection is available"""
        # We're available if either method works
        return self.xdotool_available or (self.display is not None)