"""Application detection system for intelligent text injection

Detects the active application and classifies it to select the best
injection strategy.
"""

import platform
import subprocess
from typing import Optional, List, Tuple
from dataclasses import dataclass
from .text_injection import ApplicationInfo, ApplicationType
from .logger import setup_logger

logger = setup_logger(__name__)


class ApplicationDetector:
    """Detects and classifies the active application"""
    
    def __init__(self):
        self.platform = platform.system()
        
        # Application patterns for classification
        self.editor_patterns = [
            "code", "vscode", "notepad", "notepad++", "sublime", 
            "vim", "emacs", "kate", "kwrite", "gedit", "atom",
            "brackets", "textmate"
        ]
        
        self.browser_patterns = [
            "chrome", "firefox", "edge", "safari", "opera", 
            "brave", "vivaldi", "chromium", "iexplore"
        ]
        
        self.terminal_patterns = [
            "cmd", "powershell", "terminal", "bash", "konsole", 
            "gnome-terminal", "xterm", "alacritty", "kitty", 
            "iterm", "hyper", "conemu", "cmder"
        ]
        
        self.ide_patterns = [
            "devenv", "idea", "pycharm", "webstorm", "clion",
            "rubymine", "phpstorm", "android", "xcode", "eclipse",
            "netbeans", "visualstudio"
        ]
        
        self.office_patterns = [
            "winword", "excel", "powerpnt", "outlook", "onenote",
            "libreoffice", "soffice", "writer", "calc", "impress"
        ]
        
        self.chat_patterns = [
            "slack", "discord", "teams", "skype", "telegram",
            "whatsapp", "signal", "element", "mattermost"
        ]
    
    def detect_active_window(self) -> ApplicationInfo:
        """Platform-aware active window detection"""
        if self.platform == "Windows":
            return self._detect_windows()
        elif self.platform == "Linux":
            return self._detect_linux()
        elif self.platform == "Darwin":
            return self._detect_macos()
        else:
            return ApplicationInfo(
                name="unknown",
                process_name="unknown",
                window_title="",
                app_type=ApplicationType.UNKNOWN
            )
    
    def _detect_windows(self) -> ApplicationInfo:
        """Windows-specific window detection"""
        try:
            import win32gui
            import win32process
            import psutil
            
            # Get foreground window
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return self._create_unknown_app_info()
            
            # Get window title
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process ID and name
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            try:
                process = psutil.Process(pid)
                process_name = process.name().lower()
                app_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "unknown"
                app_name = "unknown"
            
            # Classify the application
            app_type = self.classify_application(process_name, window_title)
            
            return ApplicationInfo(
                name=app_name,
                process_name=process_name,
                window_title=window_title,
                app_type=app_type,
                window_class=None,
                extra_info={"platform": "Windows", "pid": pid}
            )
            
        except Exception as e:
            logger.warning(f"Windows app detection failed: {e}")
            return self._create_unknown_app_info()
    
    def _detect_linux(self) -> ApplicationInfo:
        """Linux window detection using xdotool"""
        try:
            # Get active window ID
            window_id = subprocess.check_output(
                ['xdotool', 'getactivewindow'], 
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Get window class
            window_class = subprocess.check_output(
                ['xdotool', 'getwindowclassname', window_id],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Get window title
            window_title = subprocess.check_output(
                ['xdotool', 'getwindowname', window_id],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Get process info
            window_pid = subprocess.check_output(
                ['xdotool', 'getwindowpid', window_id],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Try to get process name
            try:
                import psutil
                process = psutil.Process(int(window_pid))
                process_name = process.name().lower()
            except:
                process_name = window_class.lower()
            
            # Classify the application
            app_type = self.classify_application(process_name, window_title)
            
            return ApplicationInfo(
                name=window_class,
                process_name=process_name,
                window_title=window_title,
                app_type=app_type,
                window_class=window_class,
                extra_info={
                    "platform": "Linux",
                    "window_id": window_id,
                    "pid": window_pid
                }
            )
            
        except subprocess.CalledProcessError:
            # xdotool not available or failed
            return self._detect_linux_alternative()
        except Exception as e:
            logger.warning(f"Linux app detection failed: {e}")
            return self._create_unknown_app_info()
    
    def _detect_linux_alternative(self) -> ApplicationInfo:
        """Alternative Linux detection using wmctrl or xprop"""
        try:
            # Try wmctrl first
            output = subprocess.check_output(
                ['wmctrl', '-l', '-p'],
                stderr=subprocess.DEVNULL
            ).decode()
            
            # Parse active window (implementation depends on window manager)
            # This is a simplified version
            lines = output.strip().split('\n')
            if lines:
                # Assume first window is active (not always true)
                parts = lines[0].split(None, 4)
                if len(parts) >= 5:
                    window_title = parts[4]
                    return ApplicationInfo(
                        name="unknown",
                        process_name="unknown",
                        window_title=window_title,
                        app_type=ApplicationType.UNKNOWN
                    )
        except:
            pass
        
        return self._create_unknown_app_info()
    
    def _detect_macos(self) -> ApplicationInfo:
        """macOS-specific window detection"""
        try:
            # Use AppleScript to get active application info
            script = '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                set windowTitle to ""
                try
                    tell process frontApp
                        set windowTitle to name of front window
                    end tell
                end try
                return frontApp & "|" & windowTitle
            end tell
            '''
            
            result = subprocess.check_output(
                ['osascript', '-e', script],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            parts = result.split('|')
            app_name = parts[0] if parts else "unknown"
            window_title = parts[1] if len(parts) > 1 else ""
            
            # Classify the application
            app_type = self.classify_application(app_name.lower(), window_title)
            
            return ApplicationInfo(
                name=app_name,
                process_name=app_name.lower(),
                window_title=window_title,
                app_type=app_type,
                extra_info={"platform": "Darwin"}
            )
            
        except Exception as e:
            logger.warning(f"macOS app detection failed: {e}")
            return self._create_unknown_app_info()
    
    def classify_application(self, process_name: str, window_title: str) -> ApplicationType:
        """Classify application based on process name and window title"""
        process_lower = process_name.lower()
        title_lower = window_title.lower()
        
        # Check process name patterns
        if any(pattern in process_lower for pattern in self.editor_patterns):
            return ApplicationType.EDITOR
        elif any(pattern in process_lower for pattern in self.browser_patterns):
            return ApplicationType.BROWSER
        elif any(pattern in process_lower for pattern in self.terminal_patterns):
            return ApplicationType.TERMINAL
        elif any(pattern in process_lower for pattern in self.ide_patterns):
            return ApplicationType.IDE
        elif any(pattern in process_lower for pattern in self.office_patterns):
            return ApplicationType.OFFICE
        elif any(pattern in process_lower for pattern in self.chat_patterns):
            return ApplicationType.CHAT
        
        # Check window title as fallback
        if any(pattern in title_lower for pattern in self.editor_patterns + ["- code", "- vim"]):
            return ApplicationType.EDITOR
        elif any(pattern in title_lower for pattern in ["mozilla", "google", "microsoft edge"]):
            return ApplicationType.BROWSER
        
        return ApplicationType.UNKNOWN
    
    def get_injection_capabilities(self, app_info: ApplicationInfo) -> dict:
        """Determine injection capabilities for the application"""
        capabilities = {
            "supports_paste": True,  # Most apps support paste
            "supports_typing": True,  # All apps support typing
            "supports_ui_automation": False,
            "prefers_clipboard": False,
            "requires_slow_typing": False,
            "injection_delay_ms": 50
        }
        
        # Adjust based on application type
        if app_info.app_type in (ApplicationType.EDITOR, ApplicationType.IDE):
            capabilities["prefers_clipboard"] = True
            capabilities["supports_ui_automation"] = True
        elif app_info.app_type == ApplicationType.BROWSER:
            capabilities["requires_slow_typing"] = True
            capabilities["injection_delay_ms"] = 100
        elif app_info.app_type == ApplicationType.TERMINAL:
            capabilities["supports_paste"] = False  # Some terminals have issues
            capabilities["requires_slow_typing"] = True
        
        return capabilities
    
    def _create_unknown_app_info(self) -> ApplicationInfo:
        """Create a default ApplicationInfo for unknown applications"""
        return ApplicationInfo(
            name="unknown",
            process_name="unknown", 
            window_title="",
            app_type=ApplicationType.UNKNOWN,
            extra_info={"platform": self.platform}
        )