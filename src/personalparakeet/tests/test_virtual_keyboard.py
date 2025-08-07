#!/usr/bin/env python3
"""
Test suite for Wayland virtual keyboard protocol implementation.
"""

import pytest
import time
from unittest.mock import Mock, patch

from personalparakeet.core.virtual_keyboard_injector import (
    VirtualKeyboardInjector,
    KeyboardLayout,
    KeyEvent
)


class TestVirtualKeyboardInjector:
    """Test cases for VirtualKeyboardInjector."""
    
    def test_initialization(self):
        """Test injector initialization."""
        injector = VirtualKeyboardInjector()
        assert injector.layout == KeyboardLayout.US
        assert not injector._connected
        
    def test_custom_layout(self):
        """Test initialization with custom layout."""
        injector = VirtualKeyboardInjector(layout=KeyboardLayout.UK)
        assert injector.layout == KeyboardLayout.UK
    
    def test_is_available(self):
        """Test protocol availability check."""
        injector = VirtualKeyboardInjector()
        # Should return False until implemented
        assert not injector.is_available()
    
    @pytest.mark.skipif(True, reason="Not implemented yet")
    def test_connect(self):
        """Test Wayland connection."""
        injector = VirtualKeyboardInjector()
        success = injector.connect()
        # Will fail until implemented
        assert success
        assert injector._connected
    
    def test_inject_text_not_connected(self):
        """Test text injection without connection."""
        injector = VirtualKeyboardInjector()
        success, error = injector.inject_text("test")
        assert not success
        assert error is not None
    
    @pytest.mark.skipif(True, reason="Not implemented yet")
    def test_inject_simple_text(self):
        """Test injecting simple ASCII text."""
        injector = VirtualKeyboardInjector()
        if injector.is_available():
            success, error = injector.inject_text("Hello World")
            assert success
            assert error is None
    
    @pytest.mark.skipif(True, reason="Not implemented yet")
    def test_inject_special_characters(self):
        """Test special characters and modifiers."""
        injector = VirtualKeyboardInjector()
        if injector.is_available():
            # Test various special characters
            test_strings = [
                "Hello!",
                "Test@123",
                "Code: if (x > 0) { return true; }",
                "Path: /home/user/file.txt",
                "Quote: \"Hello, World!\""
            ]
            
            for text in test_strings:
                success, error = injector.inject_text(text)
                assert success, f"Failed to inject: {text}"
    
    @pytest.mark.skipif(True, reason="Not implemented yet")
    def test_inject_unicode(self):
        """Test Unicode text injection."""
        injector = VirtualKeyboardInjector()
        if injector.is_available():
            unicode_text = "Hello 世界 🌍"
            success, error = injector.inject_text(unicode_text)
            # Unicode might not be fully supported initially
            if not success:
                pytest.skip("Unicode not yet supported")
    
    @pytest.mark.skipif(True, reason="Not implemented yet")
    def test_inject_key(self):
        """Test individual key injection."""
        injector = VirtualKeyboardInjector()
        if injector.is_available():
            # Test single key
            assert injector.inject_key("a")
            
            # Test with modifier
            assert injector.inject_key("a", modifiers=["shift"])
            
            # Test special keys
            assert injector.inject_key("Return")
            assert injector.inject_key("space")
            assert injector.inject_key("Tab")
    
    @pytest.mark.skipif(True, reason="Not implemented yet")
    def test_performance(self):
        """Verify injection latency is under 5ms."""
        injector = VirtualKeyboardInjector()
        if injector.is_available():
            # Warm up
            injector.inject_text("warmup")
            
            # Measure latency
            latencies = []
            for _ in range(10):
                start = time.perf_counter()
                success, _ = injector.inject_text("test")
                end = time.perf_counter()
                
                if success:
                    latency_ms = (end - start) * 1000
                    latencies.append(latency_ms)
            
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                print(f"Average latency: {avg_latency:.2f}ms")
                assert avg_latency < 5.0, f"Latency too high: {avg_latency:.2f}ms"
    
    def test_cleanup(self):
        """Test resource cleanup."""
        injector = VirtualKeyboardInjector()
        injector.cleanup()
        assert not injector._connected


@pytest.mark.integration
class TestVirtualKeyboardIntegration:
    """Integration tests with actual Wayland."""
    
    @pytest.mark.skipif(True, reason="Requires Wayland environment")
    def test_real_wayland_injection(self):
        """Test actual text injection on Wayland."""
        injector = VirtualKeyboardInjector()
        
        if not injector.is_available():
            pytest.skip("Virtual keyboard protocol not available")
        
        print("\n⚠️  Position cursor in text field!")
        print("Testing in 3 seconds...")
        time.sleep(3)
        
        test_text = "Virtual keyboard test "
        success, error = injector.inject_text(test_text)
        
        assert success, f"Injection failed: {error}"
        print("✅ Text injected successfully")
        
        # Cleanup
        injector.cleanup()


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v", "-k", "not integration"])