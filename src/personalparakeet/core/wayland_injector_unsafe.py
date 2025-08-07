"""
UNSAFE Wayland text injection - for personal use only!
This module uses every dirty trick to make text injection work.
"""

import os
import subprocess
import time
import threading
import tempfile
from typing import Tuple, Optional

import logging

logger = logging.getLogger(__name__)


class UnsafeWaylandInjector:
    """Ultra-permissive Wayland injector that tries EVERYTHING."""

    def __init__(self):
        self.last_clipboard = None
        self._setup_unsafe_mode()

    def _setup_unsafe_mode(self):
        """Set up unsafe but functional injection methods."""
        # Try to start ydotoold with sudo if not running
        try:
            # Check if ydotoold is running
            subprocess.run(["pgrep", "ydotoold"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # Not running, try to start it
            logger.info("Starting ydotoold with sudo (unsafe mode)")
            try:
                # Start in background with sudo
                subprocess.Popen(
                    ["sudo", "-n", "ydotoold"],  # -n = non-interactive
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(1)  # Give it time to start
            except:
                logger.debug("Could not start ydotoold with sudo")

    def inject_text(self, text: str) -> Tuple[bool, Optional[str]]:
        """Try every possible injection method, no matter how dirty."""

        # Method 1: Try ydotool with sudo
        if self._inject_ydotool_sudo(text):
            return True, None

        # Method 2: Create a temporary script and run with sudo
        if self._inject_via_sudo_script(text):
            return True, None

        # Method 3: Aggressive clipboard manipulation
        if self._inject_clipboard_aggressive(text):
            return True, None

        # Method 4: Try to chmod /dev/uinput (super unsafe!)
        if self._inject_with_uinput_chmod(text):
            return True, None

        # Method 5: Use xdotool even on Wayland (might work with XWayland)
        if self._inject_xdotool_anyway(text):
            return True, None

        return False, "All unsafe methods failed"

    def _inject_ydotool_sudo(self, text: str) -> bool:
        """Try ydotool with sudo."""
        try:
            # First try without sudo
            result = subprocess.run(["ydotool", "type", text], capture_output=True, timeout=2)
            if result.returncode == 0:
                return True

            # Try with sudo
            result = subprocess.run(
                ["sudo", "-n", "ydotool", "type", text], capture_output=True, timeout=2
            )
            return result.returncode == 0
        except:
            return False

    def _inject_via_sudo_script(self, text: str) -> bool:
        """Create a script and run it with sudo."""
        try:
            # Create temporary script
            with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
                escaped_text = text.replace("'", "'\"'\"'")
                script_content = f"""#!/bin/bash
# Try multiple injection methods
if command -v ydotool &> /dev/null; then
    ydotool type '{escaped_text}'
elif command -v wtype &> /dev/null; then
    wtype '{escaped_text}'
elif command -v xdotool &> /dev/null; then
    export DISPLAY=:0
    xdotool type '{escaped_text}'
fi
"""
                f.write(script_content)
                script_path = f.name

            # Make executable
            os.chmod(script_path, 0o755)

            # Run with sudo
            result = subprocess.run(["sudo", "-n", script_path], capture_output=True, timeout=2)

            # Clean up
            os.unlink(script_path)

            return result.returncode == 0
        except:
            return False

    def _inject_clipboard_aggressive(self, text: str) -> bool:
        """Aggressively manipulate clipboard with multiple paste attempts."""
        try:
            # Save current clipboard (try multiple methods)
            try:
                self.last_clipboard = subprocess.check_output(["wl-paste"], text=True, timeout=1)
            except:
                self.last_clipboard = ""

            # Copy text (try multiple methods)
            copy_success = False

            # Try wl-copy
            try:
                proc = subprocess.Popen(
                    ["wl-copy"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                proc.communicate(input=text.encode(), timeout=1)
                copy_success = proc.returncode == 0
            except:
                pass

            # Try xclip as fallback
            if not copy_success:
                try:
                    proc = subprocess.Popen(
                        ["xclip", "-selection", "clipboard"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    proc.communicate(input=text.encode(), timeout=1)
                    copy_success = proc.returncode == 0
                except:
                    pass

            if not copy_success:
                return False

            # Small delay
            time.sleep(0.1)

            # Try multiple paste methods
            paste_methods = [
                ["wtype", "-M", "ctrl", "v", "-m", "ctrl"],  # wtype
                ["ydotool", "key", "ctrl+v"],  # ydotool
                ["sudo", "-n", "ydotool", "key", "ctrl+v"],  # ydotool with sudo
                ["xdotool", "key", "ctrl+v"],  # xdotool (might work with XWayland)
                ["wtype", "-M", "shift", "Insert", "-m", "shift"],  # Alternative paste
            ]

            for method in paste_methods:
                try:
                    result = subprocess.run(method, capture_output=True, timeout=1)
                    if result.returncode == 0:
                        # Restore clipboard in background
                        threading.Thread(target=self._restore_clipboard, daemon=True).start()
                        return True
                except:
                    continue

            return False

        except Exception as e:
            logger.debug(f"Aggressive clipboard injection failed: {e}")
            return False

    def _restore_clipboard(self):
        """Restore clipboard after a delay."""
        time.sleep(0.5)
        if self.last_clipboard is not None:
            try:
                proc = subprocess.Popen(
                    ["wl-copy"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                proc.communicate(input=self.last_clipboard.encode())
            except:
                pass

    def _inject_with_uinput_chmod(self, text: str) -> bool:
        """Try to make /dev/uinput accessible (VERY UNSAFE!)."""
        try:
            # Check if we can access /dev/uinput
            if not os.path.exists("/dev/uinput"):
                return False

            # Try to chmod it (will likely fail without sudo)
            try:
                subprocess.run(
                    ["sudo", "-n", "chmod", "666", "/dev/uinput"], capture_output=True, timeout=1
                )
            except:
                pass

            # Now try ydotool again
            result = subprocess.run(["ydotool", "type", text], capture_output=True, timeout=2)

            # Restore permissions
            try:
                subprocess.run(
                    ["sudo", "-n", "chmod", "600", "/dev/uinput"], capture_output=True, timeout=1
                )
            except:
                pass

            return result.returncode == 0

        except:
            return False

    def _inject_xdotool_anyway(self, text: str) -> bool:
        """Try xdotool even on Wayland (works if app is XWayland)."""
        try:
            # Set DISPLAY if not set
            env = os.environ.copy()
            if "DISPLAY" not in env:
                env["DISPLAY"] = ":0"

            result = subprocess.run(
                ["xdotool", "type", text], capture_output=True, timeout=2, env=env
            )
            return result.returncode == 0
        except:
            return False
