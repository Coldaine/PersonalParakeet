import time
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class ClipboardManager:
    """Safely manage clipboard save/restore operations"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 0.1):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.original_content = None
        self.original_format = None
        
    def save_clipboard(self) -> bool:
        """Save current clipboard with multiple attempts"""
        for attempt in range(self.max_retries):
            try:
                # Platform-specific save implementation
                self.original_content = self._get_clipboard_content()
                self.original_format = self._get_clipboard_format()
                return True
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Failed to save clipboard after {self.max_retries} attempts: {e}")
                    return False
                time.sleep(self.retry_delay)
        return False
    
    def restore_clipboard(self) -> bool:
        """Restore clipboard with verification"""
        if self.original_content is None:
            return True  # Nothing to restore
            
        for attempt in range(self.max_retries):
            try:
                self._set_clipboard_content(self.original_content, self.original_format)
                # Verify restoration
                if self._get_clipboard_content() == self.original_content:
                    return True
            except Exception as e:
                logger.warning(f"Clipboard restore attempt {attempt + 1} failed: {e}")
                
            time.sleep(self.retry_delay)
            
        # Final fallback: notify user
        logger.error("Failed to restore clipboard. Original content may be lost.")
        return False

    # These methods need to be implemented by platform-specific subclasses
    def _get_clipboard_content(self) -> Optional[Any]:
        raise NotImplementedError

    def _get_clipboard_format(self) -> Optional[Any]:
        raise NotImplementedError

    def _set_clipboard_content(self, content: Any, format: Any):
        raise NotImplementedError