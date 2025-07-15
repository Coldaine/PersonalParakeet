"""Basic keyboard injection strategy using the keyboard library

This serves as the fallback strategy when platform-specific methods fail.
"""

import time
import keyboard
from typing import Optional
from .text_injection import TextInjectionStrategy, ApplicationInfo


class BasicKeyboardStrategy(TextInjectionStrategy):
    """Basic keyboard injection using the keyboard library"""
    
    def __init__(self):
        super().__init__()
        self.consecutive_failures = 0
        self.max_failures = 3
    
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using keyboard.write() with fallback methods
        
        Args:
            text: Text to inject
            app_info: Optional application information (not used in basic strategy)
            
        Returns:
            True if injection succeeded, False otherwise
        """
        try:
            # Add small delay to ensure focus remains on target window
            time.sleep(0.05)
            
            # Try keyboard.write first (fastest method)
            try:
                keyboard.write(text + " ")  # Add space after each word/phrase
                self.consecutive_failures = 0
                return True
            except AttributeError as e:
                # Common threading issue with keyboard.write
                print(f"⚠️  keyboard.write failed (threading issue): {e}")
                
                # Fallback to character-by-character typing
                return self._inject_by_typing(text)
                
        except Exception as e:
            print(f"❌ Basic keyboard injection failed: {type(e).__name__}: {e}")
            self.consecutive_failures += 1
            
            # If we've failed too many times, use the fallback display
            if self.consecutive_failures >= self.max_failures and self.fallback_callback:
                self.fallback_callback(text)
            
            return False
    
    def _inject_by_typing(self, text: str) -> bool:
        """Fallback method: type character by character
        
        This is slower but more compatible, especially with threading issues.
        """
        try:
            for char in text + " ":
                keyboard.press_and_release(char)
                time.sleep(0.01)  # Small delay between keystrokes for compatibility
            
            self.consecutive_failures = 0
            return True
            
        except Exception as e:
            print(f"❌ Character-by-character typing also failed: {e}")
            self.consecutive_failures += 1
            return False
    
    def is_available(self) -> bool:
        """Check if keyboard library is available and functional"""
        try:
            # Test if we can access keyboard functions
            # Note: This doesn't actually press anything, just checks the function exists
            _ = keyboard.is_pressed
            return True
        except Exception:
            return False