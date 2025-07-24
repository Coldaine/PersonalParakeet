import win32clipboard
from typing import Optional, Any
from .clipboard_manager import ClipboardManager
from .logger import setup_logger

logger = setup_logger(__name__)

class WindowsClipboardManager(ClipboardManager):
    """Windows-specific clipboard manager using win32clipboard"""

    def _get_clipboard_content(self) -> Optional[str]:
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                win32clipboard.CloseClipboard()
                return data
            win32clipboard.CloseClipboard()
        except Exception as e:
            logger.warning(f"Failed to get Windows clipboard content: {e}")
        return None

    def _get_clipboard_format(self) -> Optional[int]:
        # For simplicity, we only handle CF_UNICODETEXT for now
        return win32clipboard.CF_UNICODETEXT

    def _set_clipboard_content(self, content: str, format: Optional[int] = None):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, content)
            win32clipboard.CloseClipboard()
        except Exception as e:
            logger.error(f"Failed to set Windows clipboard content: {e}")
            raise