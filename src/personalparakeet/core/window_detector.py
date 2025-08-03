#!/usr/bin/env python3
"""
Window Detector - This module provides window change detection for thought linking.
To activate: Enable thought_linking in config

Detects when user switches between applications to help determine
if text should be linked or treated as separate contexts.
"""

import logging
import platform
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class WindowInfo:
    """Information about the current active window"""
    process_name: str
    window_title: str
    window_class: str = ""
    app_type: str = "unknown"
    window_id: Optional[int] = None


class WindowDetector:
    """
    Cross-platform window detection.
    
    Detects active window changes to inform thought linking decisions.
    """
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.platform = platform.system().lower()
        self._last_window_info: Optional[WindowInfo] = None
        
        self._platform_initialized = False
        
        logger.info(f"WindowDetector initialized (enabled={enabled}, platform={self.platform})")
        if self.enabled:
            self._initialize_platform()

    def _initialize_platform(self):
        """Initialize platform-specific dependencies"""
        if self._platform_initialized or not self.enabled:
            return
            
        try:
            if self.platform == "windows":
                self._init_windows()
            elif self.platform == "linux":
                self._init_linux()
            elif self.platform == "darwin":
                self._init_macos()
            else:
                logger.warning(f"Unsupported platform for window detection: {self.platform}")
                self.enabled = False
                
            if self.enabled:
                self._platform_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize window detection: {e}")
            self.enabled = False

    def _init_windows(self):
        """Initialize Windows-specific dependencies"""
        try:
            import win32gui
            import win32process
            import psutil
            self._win32gui = win32gui
            self._win32process = win32process
            self._psutil = psutil
            logger.debug("Windows window detection initialized")
        except ImportError:
            logger.warning("pywin32 and psutil not installed. Run 'pip install pywin32 psutil' for window detection on Windows.")
            self.enabled = False

    def _init_linux(self):
        """Initialize Linux-specific dependencies"""
        try:
            from Xlib import display, X
            import ewmh
            self._display = display.Display()
            self._ewmh = ewmh.EWMH(self._display)
            self._X = X
            logger.debug("Linux window detection initialized")
        except ImportError:
            logger.warning("python-xlib and ewmh not installed. Run 'pip install python-xlib ewmh' for window detection on Linux.")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Xlib/EWMH for window detection: {e}")
            self.enabled = False

    def _init_macos(self):
        """Initialize macOS-specific dependencies"""
        try:
            from AppKit import NSWorkspace
            self._ns_workspace = NSWorkspace.sharedWorkspace()
            logger.debug("macOS window detection initialized")
        except ImportError:
            logger.warning("pyobjc-framework-Cocoa not installed. Run 'pip install pyobjc-framework-Cocoa' for window detection on macOS.")
            self.enabled = False

    def get_current_window(self) -> Optional[WindowInfo]:
        """
        Get information about the currently active window
        
        Returns:
            WindowInfo if successful, None if disabled or error
        """
        if not self.enabled or not self._platform_initialized:
            return None

        try:
            if self.platform == "windows":
                return self._get_window_windows()
            elif self.platform == "linux":
                return self._get_window_linux()
            elif self.platform == "darwin":
                return self._get_window_macos()
        except Exception as e:
            logger.error(f"Error getting window info on {self.platform}: {e}")
            self.enabled = False # Disable on error
        return None

    def _get_window_windows(self) -> Optional[WindowInfo]:
        """Get active window on Windows"""
        hwnd = self._win32gui.GetForegroundWindow()
        if not hwnd:
            return None
        
        _, pid = self._win32process.GetWindowThreadProcessId(hwnd)
        process_name = self._psutil.Process(pid).name()
        window_title = self._win32gui.GetWindowText(hwnd)
        window_class = self._win32gui.GetClassName(hwnd)
        
        return WindowInfo(
            process_name=process_name,
            window_title=window_title,
            window_class=window_class,
            window_id=hwnd
        )

    def _get_window_linux(self) -> Optional[WindowInfo]:
        """Get active window on Linux"""
        win = self._ewmh.getActiveWindow()
        if not win:
            return None

        pid = self._ewmh.getWmPid(win)
        process_name = "unknown"
        if pid:
            try:
                import psutil
                process_name = psutil.Process(pid).name()
            except (ImportError, psutil.NoSuchProcess):
                pass # psutil might not be installed or process is gone

        window_title = self._ewmh.getWmName(win).decode('utf-8', 'ignore')
        window_class = win.get_wm_class()
        if window_class:
            window_class = window_class[1]

        return WindowInfo(
            process_name=process_name,
            window_title=window_title,
            window_class=window_class or "",
            window_id=win.id
        )

    def _get_window_macos(self) -> Optional[WindowInfo]:
        """Get active window on macOS"""
        active_app = self._ns_workspace.activeApplication()
        if not active_app:
            return None

        process_name = active_app.get('NSApplicationName', 'unknown')
        
        # Getting window title is more complex and requires accessibility permissions
        # This is a simplified approach
        window_title = ""
        try:
            from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
            options = kCGWindowListOptionOnScreenOnly
            window_list = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
            for window in window_list:
                if window.get('kCGWindowOwnerPID') == active_app.get('NSApplicationProcessIdentifier'):
                    window_title = window.get('kCGWindowName', '')
                    if window_title:
                        break
        except Exception as e:
            logger.warning(f"Could not get window title on macOS: {e}")

        return WindowInfo(
            process_name=process_name,
            window_title=window_title or f"{process_name} Window",
            app_type=active_app.get('NSApplicationBundleIdentifier', '')
        )

    def has_window_changed(self) -> bool:
        """
        Check if the active window has changed since last check
        
        Returns:
            True if window changed, False otherwise
        """
        if not self.enabled:
            return False
            
        current = self.get_current_window()
        if current is None:
            return False
            
        if self._last_window_info is None:
            self._last_window_info = current
            return True
            
        changed = (
            current.process_name != self._last_window_info.process_name or
            current.window_title != self._last_window_info.window_title
        )
        
        if changed:
            logger.debug(f"Window changed: {self._last_window_info.process_name} -> {current.process_name}")
            self._last_window_info = current
            
        return changed
    
    def get_window_context(self) -> Dict[str, Any]:
        """
        Get window context information for thought linking
        
        Returns:
            Dictionary with window context data
        """
        if not self.enabled:
            return {"enabled": False}
            
        current = self.get_current_window()
        if current is None:
            return {"enabled": True, "detected": False}
            
        return {
            "enabled": True,
            "detected": True,
            "process_name": current.process_name,
            "window_title": current.window_title,
            "app_type": current.app_type,
            "window_class": current.window_class
        }


def create_window_detector(enabled: bool = False) -> WindowDetector:
    """Factory function to create a window detector"""
    return WindowDetector(enabled=enabled)