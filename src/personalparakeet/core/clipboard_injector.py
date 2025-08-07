"""
Pure clipboard-based text injection as ultimate fallback.
Works on any system with clipboard support.
"""

import subprocess
import time
import platform
import logging

logger = logging.getLogger(__name__)


class ClipboardInjector:
    """Clipboard-based text injection that works everywhere."""

    def __init__(self):
        self.system = platform.system().lower()
        self.last_clipboard = None

    def inject_text(self, text: str) -> bool:
        """Inject text using clipboard and paste simulation."""
        try:
            # Save current clipboard
            self.last_clipboard = self._get_clipboard()

            # Set new text
            if not self._set_clipboard(text):
                return False

            # Small delay for clipboard to settle
            time.sleep(0.05)

            # Try to paste
            if not self._simulate_paste():
                # If paste fails, at least the text is in clipboard
                logger.info("Text copied to clipboard - press Ctrl+V manually")

            # Restore clipboard after delay
            if self.last_clipboard is not None:
                # Do it in background after a delay
                import threading

                threading.Timer(1.0, self._restore_clipboard).start()

            return True

        except Exception as e:
            logger.error(f"Clipboard injection failed: {e}")
            return False

    def _get_clipboard(self) -> str:
        """Get current clipboard content."""
        try:
            if self.system == "linux":
                # Try wl-paste first (Wayland)
                try:
                    return subprocess.check_output(["wl-paste"], text=True, timeout=1)
                except:
                    # Try xclip (X11)
                    return subprocess.check_output(
                        ["xclip", "-selection", "clipboard", "-o"], text=True, timeout=1
                    )
            elif self.system == "darwin":
                return subprocess.check_output(["pbpaste"], text=True, timeout=1)
            elif self.system == "windows":
                # Use PowerShell
                return subprocess.check_output(
                    ["powershell", "-command", "Get-Clipboard"], text=True, timeout=1
                )
        except:
            return ""

    def _set_clipboard(self, text: str) -> bool:
        """Set clipboard content."""
        try:
            if self.system == "linux":
                # Try wl-copy first (Wayland)
                try:
                    proc = subprocess.Popen(
                        ["wl-copy"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    proc.communicate(input=text.encode(), timeout=1)
                    return proc.returncode == 0
                except:
                    # Try xclip (X11)
                    proc = subprocess.Popen(
                        ["xclip", "-selection", "clipboard"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    proc.communicate(input=text.encode(), timeout=1)
                    return proc.returncode == 0

            elif self.system == "darwin":
                proc = subprocess.Popen(
                    ["pbcopy"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                proc.communicate(input=text.encode(), timeout=1)
                return proc.returncode == 0

            elif self.system == "windows":
                # Use PowerShell
                proc = subprocess.Popen(
                    ["powershell", "-command", "Set-Clipboard", "-Value", text],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                proc.communicate(timeout=1)
                return proc.returncode == 0

        except Exception as e:
            logger.error(f"Failed to set clipboard: {e}")
            return False

    def _simulate_paste(self) -> bool:
        """Try to simulate paste keystroke."""
        paste_commands = []

        if self.system == "linux":
            # Try various paste methods
            paste_commands = [
                # Wayland methods
                ["wtype", "-M", "ctrl", "v", "-m", "ctrl"],
                ["ydotool", "key", "ctrl+v"],
                ["wtype", "-M", "shift", "Insert", "-m", "shift"],
                # X11 methods
                ["xdotool", "key", "ctrl+v"],
                ["xdotool", "key", "shift+Insert"],
                # Even try with DISPLAY set
                ["env", "DISPLAY=:0", "xdotool", "key", "ctrl+v"],
            ]
        elif self.system == "darwin":
            paste_commands = [
                [
                    "osascript",
                    "-e",
                    'tell application "System Events" to keystroke "v" using command down',
                ],
            ]
        elif self.system == "windows":
            # On Windows, we'd use pyautogui or win32api
            # but this is meant to be a simple fallback
            return False

        # Try each paste method
        for cmd in paste_commands:
            try:
                result = subprocess.run(cmd, capture_output=True, timeout=1)
                if result.returncode == 0:
                    return True
            except:
                continue

        return False

    def _restore_clipboard(self):
        """Restore the original clipboard content."""
        try:
            if self.last_clipboard:
                self._set_clipboard(self.last_clipboard)
        except:
            pass
