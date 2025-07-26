import pytest
import subprocess
from unittest.mock import Mock, patch, AsyncMock
from personalparakeet.kde_wayland_manager import (
    KDEWaylandManager, TextInjectionMethod, WindowInfo
)


class TestKDEWaylandManager:
    """Test suite for KDE Wayland Manager"""
    
    @patch('shutil.which')
    def test_detect_kdotool_available(self, mock_which):
        """Test kdotool detection"""
        mock_which.side_effect = lambda cmd: '/usr/bin/kdotool' if cmd == 'kdotool' else None
        
        manager = KDEWaylandManager()
        assert TextInjectionMethod.KDOTOOL in manager.available_methods
    
    @patch('subprocess.run')
    @patch('shutil.which', return_value='/usr/bin/kdotool')
    def test_get_active_window_kdotool(self, mock_which, mock_run):
        """Test window detection via kdotool"""
        # Mock kdotool responses
        mock_run.side_effect = [
            Mock(stdout='12345', returncode=0),  # getactivewindow
            Mock(stdout='Test Window', returncode=0),  # getwindowname
            Mock(stdout='firefox', returncode=0),  # getwindowclassname
        ]
        
        manager = KDEWaylandManager()
        info = manager.get_active_window()
        
        assert info.title == 'Test Window'
        assert info.window_class == 'firefox'
        assert info.window_id == 12345
    
    @patch('subprocess.run')
    @patch('shutil.which', return_value='/usr/bin/kdotool')
    def test_inject_text_kdotool(self, mock_which, mock_run):
        """Test text injection via kdotool"""
        mock_run.return_value = Mock(returncode=0)
        
        manager = KDEWaylandManager()
        result = manager.inject_text("Hello World")
        
        assert result is True
        mock_run.assert_called_with(['kdotool', 'type', 'Hello World'], check=True)
    
    @pytest.mark.parametrize("malicious_input", [
        '"; workspace.exit(); "',
        '`${workspace.exit()}`',
        '\n\r\t',
        '\x00\x1b',
    ])
    def test_js_sanitization(self, malicious_input):
        """Test JavaScript injection prevention"""
        manager = KDEWaylandManager()
        sanitized = manager._sanitize_for_kwin_js(malicious_input)
        
        # Should be valid JSON string
        assert sanitized.startswith('"') and sanitized.endswith('"')
        # Should not contain unescaped quotes
        assert '";' not in sanitized[1:-1]
    
    @patch('subprocess.run')
    @patch('shutil.which')
    def test_fallback_chain(self, mock_which, mock_run):
        """Test fallback from kdotool to clipboard method"""
        # Only clipboard tools available
        mock_which.side_effect = lambda cmd: '/usr/bin/' + cmd if cmd in ['wl-copy', 'wl-paste'] else None
        
        # Mock clipboard operations
        mock_run.side_effect = [
            Mock(stdout='old content', returncode=0),  # wl-paste (get old)
            Mock(returncode=0),  # wl-copy (set new)
            Mock(returncode=1),  # kdotool key (fail - not available)
            Mock(returncode=0),  # ydotool key (simulate paste)
            Mock(returncode=0),  # restore old clipboard
        ]
        
        # Need to mock ydotool check too
        with patch.object(KDEWaylandManager, '_check_ydotool_daemon', return_value=True):
            mock_which.side_effect = lambda cmd: '/usr/bin/' + cmd if cmd in ['wl-copy', 'wl-paste', 'ydotool'] else None
            
            manager = KDEWaylandManager()
            result = manager.inject_text("Test")
            
            # Even though kdotool failed, clipboard method should succeed
            assert result is True