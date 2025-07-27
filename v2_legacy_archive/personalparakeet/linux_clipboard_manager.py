import subprocess
import time
from typing import Optional, Any
from .clipboard_manager import ClipboardManager
from .logger import setup_logger

logger = setup_logger(__name__)

class LinuxClipboardManager(ClipboardManager):
    """Linux-specific clipboard manager using xclip/xsel/wl-copy"""

    def __init__(self, max_retries: int = 3, retry_delay: float = 0.1):
        super().__init__(max_retries, retry_delay)
        self.clipboard_tool = self._detect_clipboard_tool()

    def _detect_clipboard_tool(self) -> Optional[str]:
        """Detect available clipboard tool"""
        tools = ['xclip', 'xsel', 'wl-copy']
        
        for tool in tools:
            try:
                subprocess.run([tool, '--version'], 
                             capture_output=True, check=True)
                logger.info(f"Using {tool} for clipboard operations")
                return tool
            except:
                continue
        
        logger.warning("No clipboard tool found (xclip, xsel, or wl-copy)")
        return None

    def _get_clipboard_content(self) -> Optional[str]:
        """Get current clipboard content"""
        if not self.clipboard_tool:
            return None
        try:
            if self.clipboard_tool == 'xclip':
                result = subprocess.run(
                    ['xclip', '-selection', 'clipboard', '-out'],
                    capture_output=True, text=True, check=True
                )
            elif self.clipboard_tool == 'xsel':
                result = subprocess.run(
                    ['xsel', '--clipboard', '--output'],
                    capture_output=True, text=True, check=True
                )
            elif self.clipboard_tool == 'wl-copy':
                result = subprocess.run(
                    ['wl-paste'],
                    capture_output=True, text=True, check=True
                )
            else:
                return None
                
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception as e:
            logger.warning(f"Failed to get clipboard content with {self.clipboard_tool}: {e}")
            return None

    def _get_clipboard_format(self) -> Optional[Any]:
        # For Linux, we primarily deal with plain text, so format is less critical
        return None

    def _set_clipboard_content(self, content: str, format: Optional[Any] = None):
        """Set clipboard content"""
        if not self.clipboard_tool:
            raise RuntimeError("No clipboard tool available to set content.")
        try:
            if self.clipboard_tool == 'xclip':
                process = subprocess.Popen(
                    ['xclip', '-selection', 'clipboard'],
                    stdin=subprocess.PIPE
                )
                process.communicate(content.encode('utf-8'))
            elif self.clipboard_tool == 'xsel':
                process = subprocess.Popen(
                    ['xsel', '--clipboard', '--input'],
                    stdin=subprocess.PIPE
                )
                process.communicate(content.encode('utf-8'))
            elif self.clipboard_tool == 'wl-copy':
                process = subprocess.Popen(
                    ['wl-copy'],
                    stdin=subprocess.PIPE
                )
                process.communicate(content.encode('utf-8'))
            
            # Small delay to ensure clipboard is set
            time.sleep(0.1)

        except Exception as e:
            logger.error(f"Failed to set clipboard content with {self.clipboard_tool}: {e}")
            raise

    def is_available(self) -> bool:
        """Check if clipboard access is available"""
        return self.clipboard_tool is not None