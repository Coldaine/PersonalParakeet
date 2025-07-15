"""Basic keyboard injection strategy using the keyboard library

This serves as the fallback strategy when platform-specific methods fail.
"""

import time
import keyboard
from typing import Optional
from .text_injection import TextInjectionStrategy, ApplicationInfo
from .config import InjectionConfig
from .logger import setup_logger

logger = setup_logger(__name__)


class BasicKeyboardStrategy(TextInjectionStrategy):
    """Basic keyboard injection strategy using the keyboard library.
    
    This is a universal fallback strategy, but it might not be as reliable
    or fast as platform-specific methods, especially for special characters
    or in certain applications.
    """
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        super().__init__()
        self.config = config if config is not None else InjectionConfig()

    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text by typing character by character"""
        try:
            # Add a small delay to ensure the window is ready to receive input
            time.sleep(self.config.focus_acquisition_delay)
            
            # Type the text character by character
            keyboard.write(text + " ")
            
            return True
            
        except Exception as e:
            logger.error(f"Basic keyboard injection failed: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if the keyboard library is available"""
        try:
            # Attempt to use a function from the keyboard library to check availability
            _ = keyboard.is_pressed
            return True
        except Exception:
            return False