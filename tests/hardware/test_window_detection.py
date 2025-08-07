"""Test window detection functionality."""

import platform
import time

import pytest

from tests.core import BaseHardwareTest


class TestWindowDetection(BaseHardwareTest):
    """Test window detection across platforms."""

    @pytest.mark.hardware
    def test_platform_detection(self):
        """Test platform detection."""
        system = platform.system()
        print(f"\nPlatform: {system}")
        print(f"Version: {platform.version()}")
        print(f"Architecture: {platform.machine()}")

        assert system in ["Windows", "Linux", "Darwin"], f"Unexpected platform: {system}"

    @pytest.mark.hardware
    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
    def test_windows_pygetwindow(self):
        """Test pygetwindow functionality on Windows."""
        try:
            import pygetwindow as gw
        except ImportError:
            pytest.skip("pygetwindow not installed")

        # Get all windows
        windows = gw.getAllWindows()
        print(f"\nFound {len(windows)} windows")

        # Show first few window titles
        for i, window in enumerate(windows[:5]):
            print(f"  {i+1}. {window.title}")

        assert len(windows) > 0, "No windows found"

        # Test active window
        active = gw.getActiveWindow()
        if active:
            print(f"\nActive window: {active.title}")
            print(f"  Position: ({active.left}, {active.top})")
            print(f"  Size: {active.width}x{active.height}")

    @pytest.mark.hardware
    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
    def test_windows_win32gui(self):
        """Test win32gui functionality on Windows."""
        try:
            import win32gui
        except ImportError:
            pytest.skip("win32gui not installed")

        # Get foreground window
        hwnd = win32gui.GetForegroundWindow()
        assert hwnd != 0, "No foreground window"

        # Get window text
        window_text = win32gui.GetWindowText(hwnd)
        print(f"\nForeground window: {window_text}")

        # Enumerate windows
        windows = []

        def enum_handler(hwnd, ctx):
            if win32gui.IsWindowVisible(hwnd):
                text = win32gui.GetWindowText(hwnd)
                if text:
                    windows.append(text)

        win32gui.EnumWindows(enum_handler, None)
        print(f"\nFound {len(windows)} visible windows with titles")

        assert len(windows) > 0, "No visible windows found"

    @pytest.mark.hardware
    @pytest.mark.skipif(platform.system() == "Windows", reason="Non-Windows only")
    def test_non_windows_fallback(self):
        """Test window detection fallback on non-Windows systems."""
        system = platform.system()

        if system == "Darwin":  # macOS
            try:
                from AppKit import NSWorkspace

                workspace = NSWorkspace.sharedWorkspace()
                active_app = workspace.activeApplication()
                print(f"\nActive application: {active_app['NSApplicationName']}")
                assert active_app is not None
            except ImportError:
                print("AppKit not available, skipping macOS test")

        elif system == "Linux":
            # Try to detect X11/Wayland
            import os

            display = os.environ.get("DISPLAY")
            wayland = os.environ.get("WAYLAND_DISPLAY")

            print(f"\nDisplay server:")
            if display:
                print(f"  X11 display: {display}")
            if wayland:
                print(f"  Wayland display: {wayland}")

            if not display and not wayland:
                pytest.skip("No display server detected")

    @pytest.mark.hardware
    def test_window_monitoring_performance(self):
        """Test performance of window monitoring."""
        system = platform.system()

        if system == "Windows":
            try:
                import pygetwindow as gw
            except ImportError:
                pytest.skip("pygetwindow not installed")

            # Measure time to get active window
            times = []
            for _ in range(100):
                start = time.time()
                active = gw.getActiveWindow()
                elapsed = time.time() - start
                times.append(elapsed)

            avg_time = sum(times) / len(times) * 1000  # ms
            max_time = max(times) * 1000

            print(f"\nWindow detection performance:")
            print(f"  Average: {avg_time:.2f} ms")
            print(f"  Maximum: {max_time:.2f} ms")

            # Should be fast
            assert avg_time < 10, f"Window detection too slow: {avg_time:.2f} ms"
        else:
            pytest.skip(f"Window monitoring test not implemented for {system}")
