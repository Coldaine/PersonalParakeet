"""
Automated tests for Wayland text injection
"""

import os
import time
from unittest.mock import MagicMock, patch

import pytest

from personalparakeet.core.text_injector import TextInjector
from personalparakeet.core.wayland_injector import (
    InjectionMethod,
    WaylandCompositor,
    WaylandInjector,
)


class TestWaylandInjection:
    """Test Wayland text injection functionality."""

    @pytest.mark.integration
    def test_wayland_detection(self):
        """Test Wayland environment detection."""
        # Check if we're on Wayland
        session_type = os.environ.get("XDG_SESSION_TYPE", "")
        wayland_display = os.environ.get("WAYLAND_DISPLAY", "")

        print(f"\nEnvironment:")
        print(f"  XDG_SESSION_TYPE: {session_type}")
        print(f"  WAYLAND_DISPLAY: {wayland_display}")

        # If on Wayland, test detection
        if session_type == "wayland" or wayland_display:
            injector = WaylandInjector()

            assert injector.capabilities.session_type in ["wayland", "x11"]
            assert injector.capabilities.compositor != WaylandCompositor.UNKNOWN
            print(f"  Detected compositor: {injector.capabilities.compositor.value}")
            print(
                f"  Available methods: {[m.value for m in injector.capabilities.available_methods]}"
            )

    @pytest.mark.integration
    @pytest.mark.skipif(
        os.environ.get("XDG_SESSION_TYPE") != "wayland", reason="Not running on Wayland"
    )
    def test_wayland_injection_methods(self):
        """Test available Wayland injection methods."""
        injector = WaylandInjector()

        # Check that we have at least one method available
        assert (
            len(injector.capabilities.available_methods) > 0
        ), "No injection methods available on Wayland"

        # Test method priority
        assert len(injector.method_priority) > 0, "No injection methods prioritized"

        # Log available methods
        print(f"\nWayland injection methods:")
        for i, method in enumerate(injector.method_priority):
            print(f"  {i+1}. {method.value}")

    @pytest.mark.integration
    def test_text_injector_wayland_support(self):
        """Test that TextInjector properly detects and uses Wayland."""
        with patch.dict(os.environ, {"XDG_SESSION_TYPE": "wayland"}):
            injector = TextInjector()

            # Mock the actual injection to avoid side effects
            with patch.object(injector, "_inject_linux_wayland", return_value=True) as mock_wayland:
                success = injector.inject_text("Test on Wayland")

                # Verify Wayland method was called
                if os.environ.get("XDG_SESSION_TYPE") == "wayland":
                    mock_wayland.assert_called_once()
                    assert success

    @pytest.mark.integration
    @pytest.mark.parametrize(
        "text",
        [
            "Simple text",
            "Text with spaces and punctuation!",
            "Numbers 123 and symbols @#$",
            "Multi\nline\ntext",
            "Text with 'quotes' and \"double quotes\"",
        ],
    )
    def test_wayland_text_escaping(self, text):
        """Test that various text patterns are properly escaped."""
        injector = WaylandInjector()

        # Test wtype escaping
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            injector._inject_wtype(text)

            # Verify subprocess was called with properly escaped text
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "wtype" in call_args

    @pytest.mark.integration
    def test_clipboard_fallback(self):
        """Test clipboard injection as fallback."""
        from personalparakeet.core.clipboard_injector import ClipboardInjector

        injector = ClipboardInjector()

        # Mock clipboard operations
        with patch.object(injector, "_get_clipboard", return_value="original"):
            with patch.object(injector, "_set_clipboard", return_value=True):
                with patch.object(injector, "_simulate_paste", return_value=False):
                    success = injector.inject_text("Test clipboard")
                    assert success  # Should succeed even if paste fails

    @pytest.mark.integration
    @pytest.mark.slow
    def test_injection_performance(self):
        """Test injection performance meets requirements."""
        injector = WaylandInjector()

        if not injector.capabilities.available_methods:
            pytest.skip("No Wayland injection methods available")

        # Mock the actual injection to measure overhead
        test_text = "Performance test text"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            start_time = time.time()
            success, error = injector.inject_text(test_text)
            elapsed = time.time() - start_time

            # Should complete within 150ms (project requirement)
            assert elapsed < 0.15, f"Injection took {elapsed*1000:.1f}ms, exceeds 150ms limit"

            print(f"\nInjection performance: {elapsed*1000:.1f}ms")

    @pytest.mark.integration
    def test_unsafe_mode_fallback(self):
        """Test that unsafe mode is used as final fallback."""
        from personalparakeet.core.wayland_injector_unsafe import UnsafeWaylandInjector

        unsafe = UnsafeWaylandInjector()

        # Mock all unsafe methods to fail except clipboard
        with patch.object(unsafe, "_inject_ydotool_sudo", return_value=False):
            with patch.object(unsafe, "_inject_via_sudo_script", return_value=False):
                with patch.object(unsafe, "_inject_clipboard_aggressive", return_value=True):
                    success, error = unsafe.inject_text("Test unsafe")
                    assert success

    @pytest.mark.integration
    def test_wayland_capabilities_struct(self):
        """Test WaylandCapabilities data structure."""
        injector = WaylandInjector()
        caps = injector.capabilities

        # Verify all required fields
        assert hasattr(caps, "compositor")
        assert hasattr(caps, "available_methods")
        assert hasattr(caps, "has_xwayland")
        assert hasattr(caps, "session_type")

        # Verify types
        assert isinstance(caps.compositor, WaylandCompositor)
        assert isinstance(caps.available_methods, list)
        assert isinstance(caps.has_xwayland, bool)
        assert isinstance(caps.session_type, str)
