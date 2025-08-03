"""
Enhanced Application Detection for PersonalParakeet v3

Ports the comprehensive application detection system from v2 to v3's single-process
Flet architecture with improved cross-platform support and injection optimization.
"""

import platform
import subprocess
import time
import threading
import logging
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto

logger = logging.getLogger(__name__)


class ApplicationType(Enum):
    """Application categories for injection strategy selection"""
    EDITOR = auto()      # VS Code, Sublime, Notepad++, etc.
    BROWSER = auto()     # Chrome, Firefox, Edge, etc.
    TERMINAL = auto()    # Terminal, PowerShell, CMD, etc.
    IDE = auto()         # Visual Studio, IntelliJ, PyCharm, etc.
    OFFICE = auto()      # Word, Excel, LibreOffice, etc.
    CHAT = auto()        # Slack, Discord, Teams, etc.
    UNKNOWN = auto()


@dataclass
class ApplicationInfo:
    """Information about the active application"""
    name: str
    process_name: str
    window_title: str
    app_type: ApplicationType
    window_class: Optional[str] = None
    extra_info: Optional[Dict[str, Any]] = None


@dataclass
class ApplicationProfile:
    """Complete application profile for injection optimization"""
    name: str
    process_name: str
    app_type: ApplicationType
    
    # Strategy preferences (ordered by preference)
    preferred_strategies: List[str] = field(default_factory=lambda: ["keyboard", "clipboard", "win32_sendinput"])
    
    # Performance settings
    key_delay: float = 0.01
    focus_delay: float = 0.05
    retry_attempts: int = 3
    
    # Capabilities
    supports_paste: bool = True
    supports_typing: bool = True
    supports_ui_automation: bool = True
    requires_slow_typing: bool = False
    
    # Special handling
    needs_focus_acquisition: bool = True
    paste_compatibility: str = "full"  # "full", "limited", "none"
    unicode_support: bool = True
    
    # Performance hints
    injection_delay_ms: int = 50
    max_text_length: int = 10000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for configuration"""
        return {
            "strategy_order": self.preferred_strategies,
            "key_delay": self.key_delay,
            "focus_delay": self.focus_delay,
            "retry_attempts": self.retry_attempts,
            "supports_paste": self.supports_paste,
            "supports_typing": self.supports_typing,
            "supports_ui_automation": self.supports_ui_automation,
            "requires_slow_typing": self.requires_slow_typing,
            "needs_focus_acquisition": self.needs_focus_acquisition,
            "paste_compatibility": self.paste_compatibility,
            "unicode_support": self.unicode_support,
            "injection_delay_ms": self.injection_delay_ms,
            "max_text_length": self.max_text_length
        }


class EnhancedApplicationDetector:
    """Enhanced application detector with comprehensive profiling for v3"""
    
    def __init__(self):
        self.platform = platform.system()
        self.detection_cache: Dict[str, ApplicationInfo] = {}
        self.cache_timeout = 2.0  # Cache window info for 2 seconds
        self.last_detection_time = 0
        self.last_detection_result = None
        
        # Initialize application profiles
        self.profiles = self._init_application_profiles()
        
        # Platform-specific initialization
        self._init_platform_specific()
        
        logger.info(f"Enhanced Application Detector initialized for {self.platform}")
    
    def _init_platform_specific(self):
        """Initialize platform-specific detection mechanisms"""
        if self.platform == "Windows":
            self._init_windows_detection()
        elif self.platform == "Linux":
            self._init_linux_detection()
        elif self.platform == "Darwin":
            self._init_macos_detection()
    
    def _init_windows_detection(self):
        """Initialize Windows-specific detection"""
        try:
            import ctypes
            from ctypes import wintypes
            self.user32 = ctypes.windll.user32
            self.kernel32 = ctypes.windll.kernel32
            self.has_win32 = True
            logger.info("Windows API detection available")
        except Exception as e:
            self.has_win32 = False
            logger.warning(f"Windows API not available: {e}")
    
    def _init_linux_detection(self):
        """Initialize Linux-specific detection"""
        # Check for X11 tools
        self.has_xprop = self._check_command_available("xprop")
        self.has_xdotool = self._check_command_available("xdotool")
        self.has_qdbus = self._check_command_available("qdbus")
        
        logger.info(f"Linux detection - xprop: {self.has_xprop}, xdotool: {self.has_xdotool}, qdbus: {self.has_qdbus}")
    
    def _init_macos_detection(self):
        """Initialize macOS-specific detection"""
        self.has_osascript = self._check_command_available("osascript")
        logger.info(f"macOS detection - osascript: {self.has_osascript}")
    
    def _check_command_available(self, command: str) -> bool:
        """Check if a command is available in the system"""
        try:
            subprocess.run([command, "--version"], capture_output=True, timeout=2)
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def detect_current_application(self) -> Optional[ApplicationInfo]:
        """
        Detect the currently active application with caching
        
        Returns:
            ApplicationInfo object or None if detection fails
        """
        current_time = time.time()
        
        # Use cache if recent detection available
        if (self.last_detection_result and 
            current_time - self.last_detection_time < self.cache_timeout):
            return self.last_detection_result
        
        # Perform new detection
        app_info = None
        try:
            if self.platform == "Windows":
                app_info = self._detect_windows_application()
            elif self.platform == "Linux":
                app_info = self._detect_linux_application()
            elif self.platform == "Darwin":
                app_info = self._detect_macos_application()
        except Exception as e:
            logger.error(f"Application detection failed: {e}")
        
        # Update cache
        self.last_detection_time = current_time
        self.last_detection_result = app_info
        
        if app_info:
            logger.debug(f"Detected application: {app_info.name} ({app_info.app_type.name})")
        
        return app_info
    
    def _detect_windows_application(self) -> Optional[ApplicationInfo]:
        """Detect active Windows application"""
        if not self.has_win32:
            return None
        
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get foreground window
            hwnd = self.user32.GetForegroundWindow()
            if not hwnd:
                return None
            
            # Get window title
            title_length = self.user32.GetWindowTextLengthW(hwnd)
            title_buffer = ctypes.create_unicode_buffer(title_length + 1)
            self.user32.GetWindowTextW(hwnd, title_buffer, title_length + 1)
            window_title = title_buffer.value
            
            # Get process ID
            process_id = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            
            # Get process name
            process_handle = self.kernel32.OpenProcess(0x1000, False, process_id.value)  # PROCESS_QUERY_LIMITED_INFORMATION
            if process_handle:
                try:
                    name_buffer = ctypes.create_unicode_buffer(260)  # MAX_PATH
                    name_size = wintypes.DWORD(260)
                    if self.kernel32.QueryFullProcessImageNameW(process_handle, 0, name_buffer, ctypes.byref(name_size)):
                        full_path = name_buffer.value
                        process_name = full_path.split("\\")[-1].lower()
                    else:
                        process_name = "unknown.exe"
                finally:
                    self.kernel32.CloseHandle(process_handle)
            else:
                process_name = "unknown.exe"
            
            # Get window class
            class_buffer = ctypes.create_unicode_buffer(256)
            self.user32.GetClassNameW(hwnd, class_buffer, 256)
            window_class = class_buffer.value
            
            # Classify application
            app_type = self._classify_application(process_name, window_title, window_class)
            
            return ApplicationInfo(
                name=process_name.replace('.exe', '').title(),
                process_name=process_name,
                window_title=window_title,
                app_type=app_type,
                window_class=window_class,
                extra_info={'hwnd': hwnd, 'process_id': process_id.value}
            )
            
        except Exception as e:
            logger.error(f"Windows application detection failed: {e}")
            return None
    
    def _detect_linux_application(self) -> Optional[ApplicationInfo]:
        """Detect active Linux application"""
        if not (self.has_xprop or self.has_xdotool):
            return None
        
        try:
            # Get active window ID
            if self.has_xdotool:
                result = subprocess.run(['xdotool', 'getactivewindow'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode != 0:
                    return None
                window_id = result.stdout.strip()
            else:
                return None
            
            # Get window properties
            if self.has_xprop:
                result = subprocess.run(['xprop', '-id', window_id], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode != 0:
                    return None
                
                properties = result.stdout
                
                # Parse properties
                window_title = self._extract_xprop_value(properties, 'WM_NAME')
                window_class_raw = self._extract_xprop_value(properties, 'WM_CLASS')
                
                # Parse WM_CLASS properly - it's "instance", "class"
                window_class = ""
                process_name = "unknown"
                if window_class_raw:
                    # Split on comma and take first part (instance)
                    parts = window_class_raw.split(',')
                    if parts:
                        window_class = parts[0].strip().strip('"')
                        process_name = window_class.lower()
                    if len(parts) > 1:
                        # Use the class name if available
                        class_name = parts[1].strip().strip('"')
                        if class_name:
                            window_class = class_name
                
                # Classify application
                app_type = self._classify_application(process_name, window_title, window_class)
                
                return ApplicationInfo(
                    name=process_name.title(),
                    process_name=process_name,
                    window_title=window_title,
                    app_type=app_type,
                    window_class=window_class,
                    extra_info={'window_id': window_id}
                )
            
        except Exception as e:
            logger.error(f"Linux application detection failed: {e}")
            return None
        
        return None
    
    def _detect_macos_application(self) -> Optional[ApplicationInfo]:
        """Detect active macOS application"""
        if not self.has_osascript:
            return None
        
        try:
            # Get frontmost application
            script = 'tell application "System Events" to get name of first application process whose frontmost is true'
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=2)
            
            if result.returncode != 0:
                return None
            
            app_name = result.stdout.strip()
            process_name = app_name.lower()
            
            # Get window title (if possible)
            title_script = f'tell application "System Events" to get title of front window of application process "{app_name}"'
            title_result = subprocess.run(['osascript', '-e', title_script], 
                                        capture_output=True, text=True, timeout=2)
            
            window_title = title_result.stdout.strip() if title_result.returncode == 0 else ""
            
            # Classify application
            app_type = self._classify_application(process_name, window_title)
            
            return ApplicationInfo(
                name=app_name,
                process_name=process_name,
                window_title=window_title,
                app_type=app_type,
                extra_info={'bundle_id': None}  # Could be enhanced to get bundle ID
            )
            
        except Exception as e:
            logger.error(f"macOS application detection failed: {e}")
            return None
    
    def _extract_xprop_value(self, properties: str, property_name: str) -> str:
        """Extract a property value from xprop output"""
        for line in properties.split('\n'):
            if line.startswith(property_name):
                # Extract value after = sign, removing quotes
                value = line.split('=', 1)[1].strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                return value
        return ""
    
    def _classify_application(self, process_name: str, window_title: str = "", window_class: str = "") -> ApplicationType:
        """
        Classify application based on process name, window title, and class
        
        Args:
            process_name: Name of the process/executable
            window_title: Title of the active window
            window_class: Window class (if available)
            
        Returns:
            ApplicationType enum value
        """
        process_lower = process_name.lower()
        title_lower = window_title.lower()
        class_lower = window_class.lower()
        
        # Editor applications
        editor_patterns = [
            'code', 'notepad++', 'sublime', 'atom', 'vim', 'emacs', 'nano',
            'notepad', 'gedit', 'kate', 'text'
        ]
        if any(pattern in process_lower for pattern in editor_patterns):
            return ApplicationType.EDITOR
        
        # Browser applications
        browser_patterns = [
            'chrome', 'firefox', 'edge', 'safari', 'opera', 'brave',
            'chromium', 'vivaldi', 'tor'
        ]
        if any(pattern in process_lower for pattern in browser_patterns):
            return ApplicationType.BROWSER
        
        # Terminal applications
        terminal_patterns = [
            'terminal', 'cmd', 'powershell', 'bash', 'zsh', 'fish',
            'konsole', 'gnome-terminal', 'xterm', 'iterm', 'wt'
        ]
        if any(pattern in process_lower for pattern in terminal_patterns):
            return ApplicationType.TERMINAL
        
        # IDE applications
        ide_patterns = [
            'visual studio', 'intellij', 'pycharm', 'webstorm', 'phpstorm',
            'eclipse', 'netbeans', 'xcode', 'android studio'
        ]
        if any(pattern in process_lower for pattern in ide_patterns):
            return ApplicationType.IDE
        
        # Office applications
        office_patterns = [
            'word', 'excel', 'powerpoint', 'outlook', 'onenote',
            'libreoffice', 'openoffice', 'writer', 'calc', 'impress'
        ]
        if any(pattern in process_lower for pattern in office_patterns):
            return ApplicationType.OFFICE
        
        # Chat applications
        chat_patterns = [
            'slack', 'discord', 'teams', 'zoom', 'skype', 'telegram',
            'whatsapp', 'signal', 'element', 'riot'
        ]
        if any(pattern in process_lower for pattern in chat_patterns):
            return ApplicationType.CHAT
        
        return ApplicationType.UNKNOWN
    
    def get_application_profile(self, app_info: ApplicationInfo) -> ApplicationProfile:
        """
        Get optimized injection profile for the given application
        
        Args:
            app_info: Application information
            
        Returns:
            ApplicationProfile with optimized settings
        """
        if not app_info:
            return self._get_default_profile()
        
        # Check for specific application profiles first
        profile_key = app_info.process_name.lower()
        if profile_key in self.profiles:
            return self.profiles[profile_key]
        
        # Fall back to application type profiles
        type_key = f"type_{app_info.app_type.name.lower()}"
        if type_key in self.profiles:
            return self.profiles[type_key]
        
        # Return default profile
        return self._get_default_profile()
    
    def _init_application_profiles(self) -> Dict[str, ApplicationProfile]:
        """Initialize application-specific injection profiles"""
        profiles = {}
        
        # Specific application profiles
        profiles['code.exe'] = ApplicationProfile(
            name="VS Code",
            process_name="code.exe",
            app_type=ApplicationType.EDITOR,
            preferred_strategies=["keyboard", "clipboard"],
            key_delay=0.005,
            focus_delay=0.02,
            supports_paste=True,
            unicode_support=True,
            injection_delay_ms=20
        )
        
        profiles['chrome.exe'] = ApplicationProfile(
            name="Google Chrome",
            process_name="chrome.exe",
            app_type=ApplicationType.BROWSER,
            preferred_strategies=["keyboard", "clipboard"],
            key_delay=0.01,
            focus_delay=0.05,
            supports_paste=True,
            unicode_support=True,
            injection_delay_ms=30
        )
        
        profiles['cmd.exe'] = ApplicationProfile(
            name="Command Prompt",
            process_name="cmd.exe",
            app_type=ApplicationType.TERMINAL,
            preferred_strategies=["keyboard", "win32_sendinput"],
            key_delay=0.02,
            focus_delay=0.1,
            supports_paste=False,  # Paste might not work reliably
            requires_slow_typing=True,
            injection_delay_ms=100
        )
        
        profiles['powershell.exe'] = ApplicationProfile(
            name="PowerShell",
            process_name="powershell.exe",
            app_type=ApplicationType.TERMINAL,
            preferred_strategies=["keyboard", "clipboard"],
            key_delay=0.01,
            focus_delay=0.05,
            supports_paste=True,
            unicode_support=True,
            injection_delay_ms=50
        )
        
        # Application type profiles (fallbacks)
        profiles['type_editor'] = ApplicationProfile(
            name="Generic Editor",
            process_name="editor",
            app_type=ApplicationType.EDITOR,
            preferred_strategies=["keyboard", "clipboard"],
            key_delay=0.01,
            focus_delay=0.03,
            supports_paste=True,
            unicode_support=True
        )
        
        profiles['type_browser'] = ApplicationProfile(
            name="Generic Browser",
            process_name="browser",
            app_type=ApplicationType.BROWSER,
            preferred_strategies=["keyboard", "clipboard"],
            key_delay=0.01,
            focus_delay=0.05,
            supports_paste=True,
            unicode_support=True
        )
        
        profiles['type_terminal'] = ApplicationProfile(
            name="Generic Terminal",
            process_name="terminal",
            app_type=ApplicationType.TERMINAL,
            preferred_strategies=["keyboard"],
            key_delay=0.02,
            focus_delay=0.1,
            requires_slow_typing=True,
            paste_compatibility="limited"
        )
        
        profiles['type_office'] = ApplicationProfile(
            name="Generic Office",
            process_name="office",
            app_type=ApplicationType.OFFICE,
            preferred_strategies=["keyboard", "clipboard"],
            key_delay=0.01,
            focus_delay=0.05,
            supports_paste=True,
            unicode_support=True
        )
        
        return profiles
    
    def _get_default_profile(self) -> ApplicationProfile:
        """Get default application profile for unknown applications"""
        return ApplicationProfile(
            name="Default Application",
            process_name="unknown",
            app_type=ApplicationType.UNKNOWN,
            preferred_strategies=["keyboard", "clipboard", "win32_sendinput"],
            key_delay=0.01,
            focus_delay=0.05,
            supports_paste=True,
            unicode_support=True
        )
    
    def get_optimized_strategy_order(self, app_info: ApplicationInfo) -> List[str]:
        """
        Get optimized injection strategy order for the given application
        
        Args:
            app_info: Application information
            
        Returns:
            List of strategy names in order of preference
        """
        profile = self.get_application_profile(app_info)
        return profile.preferred_strategies.copy()
    
    def get_detector_status(self) -> Dict[str, Any]:
        """Get current detector status and capabilities"""
        status = {
            'platform': self.platform,
            'cache_timeout': self.cache_timeout,
            'profiles_loaded': len(self.profiles),
            'last_detection': self.last_detection_time,
            'cached_app': self.last_detection_result.name if self.last_detection_result else None
        }
        
        # Platform-specific status
        if self.platform == "Windows":
            status['has_win32'] = getattr(self, 'has_win32', False)
        elif self.platform == "Linux":
            status.update({
                'has_xprop': getattr(self, 'has_xprop', False),
                'has_xdotool': getattr(self, 'has_xdotool', False),
                'has_qdbus': getattr(self, 'has_qdbus', False)
            })
        elif self.platform == "Darwin":
            status['has_osascript'] = getattr(self, 'has_osascript', False)
        
        return status