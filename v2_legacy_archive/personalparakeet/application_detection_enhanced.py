"""Enhanced application detection system for PersonalParakeet

This module provides comprehensive application detection with:
- Robust cross-platform window detection
- Application classification and profiling
- Strategy optimization based on detected applications
- Integration with configuration system
"""

import platform
import subprocess
import time
import threading
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from .text_injection import ApplicationInfo, ApplicationType
from .logger import setup_logger
from .constants import LogEmoji

logger = setup_logger(__name__)


@dataclass
class ApplicationProfile:
    """Complete application profile for injection optimization"""
    name: str
    process_name: str
    app_type: ApplicationType
    
    # Strategy preferences
    preferred_strategies: List[str] = field(default_factory=lambda: ["ui_automation", "keyboard", "clipboard"])
    
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
    """Enhanced application detector with comprehensive profiling"""
    
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
            import win32gui
            import win32process
            import psutil
            self.windows_modules = {
                'win32gui': win32gui,
                'win32process': win32process,
                'psutil': psutil
            }
            logger.info(f"{LogEmoji.SUCCESS} Windows detection modules loaded")
        except ImportError as e:
            logger.warning(f"{LogEmoji.WARNING} Windows detection limited: {e}")
            self.windows_modules = {}
    
    def _init_linux_detection(self):
        """Initialize Linux-specific detection"""
        self.linux_tools = {}
        
        # Check for xdotool
        try:
            subprocess.check_output(['xdotool', '--version'], stderr=subprocess.DEVNULL)
            self.linux_tools['xdotool'] = True
            logger.info(f"{LogEmoji.SUCCESS} xdotool available for Linux detection")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.linux_tools['xdotool'] = False
        
        # Check for wmctrl
        try:
            subprocess.check_output(['wmctrl', '--version'], stderr=subprocess.DEVNULL)
            self.linux_tools['wmctrl'] = True
            logger.info(f"{LogEmoji.SUCCESS} wmctrl available for Linux detection")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.linux_tools['wmctrl'] = False
        
        # Check for xprop
        try:
            subprocess.check_output(['xprop', '-version'], stderr=subprocess.DEVNULL)
            self.linux_tools['xprop'] = True
            logger.info(f"{LogEmoji.SUCCESS} xprop available for Linux detection")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.linux_tools['xprop'] = False
    
    def _init_macos_detection(self):
        """Initialize macOS-specific detection"""
        # macOS detection uses AppleScript, which is always available
        logger.info(f"{LogEmoji.SUCCESS} macOS detection initialized")
    
    def detect_active_window(self) -> ApplicationInfo:
        """Detect active window with caching"""
        current_time = time.time()
        
        # Use cached result if recent
        if (self.last_detection_result and 
            current_time - self.last_detection_time < self.cache_timeout):
            return self.last_detection_result
        
        # Perform new detection
        app_info = self._detect_active_window_uncached()
        
        # Cache result
        self.last_detection_result = app_info
        self.last_detection_time = current_time
        
        return app_info
    
    def _detect_active_window_uncached(self) -> ApplicationInfo:
        """Platform-aware active window detection without caching"""
        if self.platform == "Windows":
            return self._detect_windows_enhanced()
        elif self.platform == "Linux":
            return self._detect_linux_enhanced()
        elif self.platform == "Darwin":
            return self._detect_macos_enhanced()
        else:
            return self._create_unknown_app_info()
    
    def _detect_windows_enhanced(self) -> ApplicationInfo:
        """Enhanced Windows window detection"""
        if not self.windows_modules:
            return self._create_unknown_app_info()
        
        try:
            win32gui = self.windows_modules['win32gui']
            win32process = self.windows_modules['win32process']
            psutil = self.windows_modules['psutil']
            
            # Get foreground window
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return self._create_unknown_app_info()
            
            # Get window information
            window_title = win32gui.GetWindowText(hwnd)
            window_class = win32gui.GetClassName(hwnd)
            
            # Get process information
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            try:
                process = psutil.Process(pid)
                process_name = process.name().lower()
                app_name = process.name()
                
                # Get additional process info
                try:
                    exe_path = process.exe()
                    cmdline = process.cmdline()
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    exe_path = None
                    cmdline = []
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "unknown"
                app_name = "unknown"
                exe_path = None
                cmdline = []
            
            # Enhanced classification
            app_type = self._classify_application_enhanced(
                process_name, window_title, window_class, exe_path
            )
            
            return ApplicationInfo(
                name=app_name,
                process_name=process_name,
                window_title=window_title,
                app_type=app_type,
                window_class=window_class,
                extra_info={
                    "platform": "Windows",
                    "pid": pid,
                    "hwnd": hwnd,
                    "exe_path": exe_path,
                    "cmdline": cmdline
                }
            )
            
        except Exception as e:
            logger.warning(f"{LogEmoji.WARNING} Windows detection failed: {e}")
            return self._create_unknown_app_info()
    
    def _detect_linux_enhanced(self) -> ApplicationInfo:
        """Enhanced Linux window detection"""
        # Try xdotool first (most reliable)
        if self.linux_tools.get('xdotool'):
            result = self._detect_linux_xdotool()
            if result.app_type != ApplicationType.UNKNOWN:
                return result
        
        # Try wmctrl as fallback
        if self.linux_tools.get('wmctrl'):
            result = self._detect_linux_wmctrl()
            if result.app_type != ApplicationType.UNKNOWN:
                return result
        
        # Try xprop as last resort
        if self.linux_tools.get('xprop'):
            result = self._detect_linux_xprop()
            if result.app_type != ApplicationType.UNKNOWN:
                return result
        
        return self._create_unknown_app_info()
    
    def _detect_linux_xdotool(self) -> ApplicationInfo:
        """Linux detection using xdotool"""
        try:
            # Get active window ID
            window_id = subprocess.check_output(
                ['xdotool', 'getactivewindow'], 
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Get window information
            window_class = subprocess.check_output(
                ['xdotool', 'getwindowclassname', window_id],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            window_title = subprocess.check_output(
                ['xdotool', 'getwindowname', window_id],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Get process info
            window_pid = subprocess.check_output(
                ['xdotool', 'getwindowpid', window_id],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            # Get process name
            process_name = "unknown"
            exe_path = None
            try:
                import psutil
                process = psutil.Process(int(window_pid))
                process_name = process.name().lower()
                exe_path = process.exe()
            except:
                process_name = window_class.lower()
            
            # Enhanced classification
            app_type = self._classify_application_enhanced(
                process_name, window_title, window_class, exe_path
            )
            
            return ApplicationInfo(
                name=window_class,
                process_name=process_name,
                window_title=window_title,
                app_type=app_type,
                window_class=window_class,
                extra_info={
                    "platform": "Linux",
                    "window_id": window_id,
                    "pid": window_pid,
                    "exe_path": exe_path,
                    "detection_method": "xdotool"
                }
            )
            
        except Exception as e:
            logger.debug(f"{LogEmoji.INFO} xdotool detection failed: {e}")
            return self._create_unknown_app_info()
    
    def _detect_linux_wmctrl(self) -> ApplicationInfo:
        """Linux detection using wmctrl"""
        try:
            # Get window list with PIDs
            output = subprocess.check_output(
                ['wmctrl', '-l', '-p'],
                stderr=subprocess.DEVNULL
            ).decode()
            
            # Parse output to find active window (simplified)
            lines = output.strip().split('\n')
            if lines:
                # This is a simplified approach - proper implementation would
                # need to determine which window is actually active
                parts = lines[0].split(None, 4)
                if len(parts) >= 5:
                    window_id = parts[0]
                    desktop = parts[1]
                    pid = parts[2]
                    hostname = parts[3]
                    window_title = parts[4]
                    
                    # Get process name
                    process_name = "unknown"
                    try:
                        import psutil
                        process = psutil.Process(int(pid))
                        process_name = process.name().lower()
                    except:
                        pass
                    
                    app_type = self._classify_application_enhanced(
                        process_name, window_title, None, None
                    )
                    
                    return ApplicationInfo(
                        name=process_name,
                        process_name=process_name,
                        window_title=window_title,
                        app_type=app_type,
                        extra_info={
                            "platform": "Linux",
                            "window_id": window_id,
                            "pid": pid,
                            "detection_method": "wmctrl"
                        }
                    )
        
        except Exception as e:
            logger.debug(f"{LogEmoji.INFO} wmctrl detection failed: {e}")
        
        return self._create_unknown_app_info()
    
    def _detect_linux_xprop(self) -> ApplicationInfo:
        """Linux detection using xprop"""
        try:
            # Get active window properties
            output = subprocess.check_output(
                ['xprop', '-root', '_NET_ACTIVE_WINDOW'],
                stderr=subprocess.DEVNULL
            ).decode()
            
            # Parse window ID from output
            if 'window id' in output:
                window_id = output.split()[-1]
                
                # Get window name
                name_output = subprocess.check_output(
                    ['xprop', '-id', window_id, 'WM_NAME'],
                    stderr=subprocess.DEVNULL
                ).decode()
                
                window_title = ""
                if '=' in name_output:
                    window_title = name_output.split('=', 1)[1].strip().strip('"')
                
                # Get window class
                class_output = subprocess.check_output(
                    ['xprop', '-id', window_id, 'WM_CLASS'],
                    stderr=subprocess.DEVNULL
                ).decode()
                
                window_class = ""
                if '=' in class_output:
                    class_parts = class_output.split('=', 1)[1].strip().strip('"').split('", "')
                    if class_parts:
                        window_class = class_parts[-1].strip('"')
                
                app_type = self._classify_application_enhanced(
                    window_class.lower(), window_title, window_class, None
                )
                
                return ApplicationInfo(
                    name=window_class,
                    process_name=window_class.lower(),
                    window_title=window_title,
                    app_type=app_type,
                    window_class=window_class,
                    extra_info={
                        "platform": "Linux",
                        "window_id": window_id,
                        "detection_method": "xprop"
                    }
                )
        
        except Exception as e:
            logger.debug(f"{LogEmoji.INFO} xprop detection failed: {e}")
        
        return self._create_unknown_app_info()
    
    def _detect_macos_enhanced(self) -> ApplicationInfo:
        """Enhanced macOS window detection"""
        try:
            # Enhanced AppleScript for more information
            script = '''
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set appName to name of frontApp
                set appBundle to bundle identifier of frontApp
                set windowTitle to ""
                try
                    tell frontApp
                        set windowTitle to name of front window
                    end tell
                end try
                return appName & "|" & appBundle & "|" & windowTitle
            end tell
            '''
            
            result = subprocess.check_output(
                ['osascript', '-e', script],
                stderr=subprocess.DEVNULL
            ).decode().strip()
            
            parts = result.split('|')
            app_name = parts[0] if parts else "unknown"
            bundle_id = parts[1] if len(parts) > 1 else ""
            window_title = parts[2] if len(parts) > 2 else ""
            
            # Enhanced classification
            app_type = self._classify_application_enhanced(
                app_name.lower(), window_title, None, bundle_id
            )
            
            return ApplicationInfo(
                name=app_name,
                process_name=app_name.lower(),
                window_title=window_title,
                app_type=app_type,
                extra_info={
                    "platform": "Darwin",
                    "bundle_id": bundle_id
                }
            )
            
        except Exception as e:
            logger.warning(f"{LogEmoji.WARNING} macOS detection failed: {e}")
            return self._create_unknown_app_info()
    
    def _classify_application_enhanced(self, process_name: str, window_title: str, 
                                     window_class: Optional[str], 
                                     exe_path_or_bundle: Optional[str]) -> ApplicationType:
        """Enhanced application classification"""
        process_lower = process_name.lower()
        title_lower = window_title.lower() if window_title else ""
        class_lower = window_class.lower() if window_class else ""
        path_lower = exe_path_or_bundle.lower() if exe_path_or_bundle else ""
        
        # Check against known profiles first
        for profile in self.profiles.values():
            if profile.process_name == process_lower:
                return profile.app_type
        
        # Enhanced pattern matching - prioritize process name
        process_text = process_lower
        all_text = f"{process_lower} {title_lower} {class_lower} {path_lower}"
        
        # Check process name first for specific applications
        # Chat applications - check first to avoid conflicts with Electron apps
        if any(pattern in process_text for pattern in [
            'slack', 'discord', 'teams', 'skype', 'telegram', 'whatsapp',
            'signal', 'element', 'mattermost', 'riot', 'zoom', 'meet',
            'hangouts', 'messenger', 'viber', 'line', 'wechat', 'qq',
            'pidgin', 'hexchat', 'irssi', 'weechat', 'xchat', 'thunderbird'
        ]):
            return ApplicationType.CHAT
        
        # Check for specific office applications first (to avoid conflicts)
        if any(pattern in all_text for pattern in [
            'winword', 'excel', 'powerpnt', 'outlook', 'onenote', 'access',
            'libreoffice', 'soffice', 'writer', 'calc', 'impress', 'draw',
            'math', 'base', 'openoffice', 'abiword', 'gnumeric', 'koffice',
            'calligra', 'focuswriter', 'typora', 'marktext', 'ghostwriter',
            'powerpoint', 'microsoft word', 'microsoft office'
        ]):
            return ApplicationType.OFFICE
        
        # IDEs - check before editors (more specific)
        if any(pattern in all_text for pattern in [
            'devenv', 'idea', 'pycharm', 'webstorm', 'clion', 'rubymine',
            'phpstorm', 'android', 'xcode', 'eclipse', 'netbeans',
            'visualstudio', 'qtcreator', 'kdevelop', 'codeblocks',
            'devcpp', 'lazarus', 'monodevelop'
        ]):
            return ApplicationType.IDE
        
        # Editors - expanded patterns
        if any(pattern in all_text for pattern in [
            'code', 'vscode', 'notepad', 'sublime', 'vim', 'emacs', 'nano',
            'kate', 'kwrite', 'gedit', 'atom', 'brackets', 'textmate',
            'micro', 'joe', 'leafpad', 'mousepad', 'pluma', 'xed'
        ]):
            return ApplicationType.EDITOR
        
        # Browsers - expanded patterns
        if any(pattern in all_text for pattern in [
            'chrome', 'firefox', 'edge', 'safari', 'opera', 'brave',
            'vivaldi', 'chromium', 'iexplore', 'msedge', 'tor',
            'waterfox', 'seamonkey', 'palemoon', 'falkon', 'midori'
        ]):
            return ApplicationType.BROWSER
        
        # Terminals - expanded patterns
        if any(pattern in all_text for pattern in [
            'cmd', 'powershell', 'terminal', 'bash', 'konsole', 'gnome-terminal',
            'xterm', 'alacritty', 'kitty', 'iterm', 'hyper', 'conemu',
            'cmder', 'mintty', 'terminator', 'tilix', 'rxvt', 'urxvt',
            'st', 'sakura', 'lxterminal', 'mate-terminal', 'terminology'
        ]):
            return ApplicationType.TERMINAL
        
        # Special handling for specific window titles
        if any(keyword in title_lower for keyword in ['sql', 'database', 'mysql', 'postgres']):
            return ApplicationType.IDE
        
        if any(keyword in title_lower for keyword in ['admin', 'server', 'management']):
            return ApplicationType.OFFICE
        
        return ApplicationType.UNKNOWN
    
    def get_application_profile(self, app_info: ApplicationInfo) -> ApplicationProfile:
        """Get application profile for optimization"""
        # Check for exact match first
        profile_key = f"{app_info.process_name}_{app_info.app_type.name}"
        if profile_key in self.profiles:
            return self.profiles[profile_key]
        
        # Check for process name match
        process_matches = [p for p in self.profiles.values() 
                          if p.process_name == app_info.process_name]
        if process_matches:
            return process_matches[0]
        
        # Return type-based profile
        return self._get_default_profile_for_type(app_info.app_type)
    
    def _get_default_profile_for_type(self, app_type: ApplicationType) -> ApplicationProfile:
        """Get default profile for application type"""
        profiles = {
            ApplicationType.EDITOR: ApplicationProfile(
                name="Generic Editor",
                process_name="editor",
                app_type=app_type,
                preferred_strategies=["clipboard", "ui_automation", "keyboard"],
                key_delay=0.005,
                supports_ui_automation=True,
                paste_compatibility="full"
            ),
            ApplicationType.IDE: ApplicationProfile(
                name="Generic IDE",
                process_name="ide",
                app_type=app_type,
                preferred_strategies=["clipboard", "ui_automation", "keyboard"],
                key_delay=0.005,
                supports_ui_automation=True,
                paste_compatibility="full"
            ),
            ApplicationType.BROWSER: ApplicationProfile(
                name="Generic Browser",
                process_name="browser",
                app_type=app_type,
                preferred_strategies=["keyboard", "ui_automation", "send_input"],
                key_delay=0.015,
                requires_slow_typing=True,
                injection_delay_ms=100
            ),
            ApplicationType.TERMINAL: ApplicationProfile(
                name="Generic Terminal",
                process_name="terminal",
                app_type=app_type,
                preferred_strategies=["keyboard", "send_input"],
                key_delay=0.02,
                supports_paste=False,
                requires_slow_typing=True,
                paste_compatibility="limited"
            ),
            ApplicationType.OFFICE: ApplicationProfile(
                name="Generic Office",
                process_name="office",
                app_type=app_type,
                preferred_strategies=["ui_automation", "clipboard", "keyboard"],
                key_delay=0.01,
                supports_ui_automation=True,
                paste_compatibility="full"
            ),
            ApplicationType.CHAT: ApplicationProfile(
                name="Generic Chat",
                process_name="chat",
                app_type=app_type,
                preferred_strategies=["keyboard", "clipboard", "ui_automation"],
                key_delay=0.01,
                paste_compatibility="full"
            )
        }
        
        return profiles.get(app_type, ApplicationProfile(
            name="Unknown Application",
            process_name="unknown",
            app_type=ApplicationType.UNKNOWN,
            preferred_strategies=["keyboard", "ui_automation", "clipboard"],
            key_delay=0.01
        ))
    
    def _init_application_profiles(self) -> Dict[str, ApplicationProfile]:
        """Initialize specific application profiles"""
        profiles = {}
        
        # Popular editors
        profiles["code_EDITOR"] = ApplicationProfile(
            name="Visual Studio Code",
            process_name="code",
            app_type=ApplicationType.EDITOR,
            preferred_strategies=["clipboard", "ui_automation", "keyboard"],
            key_delay=0.003,
            supports_ui_automation=True,
            paste_compatibility="full"
        )
        
        profiles["notepad++_EDITOR"] = ApplicationProfile(
            name="Notepad++",
            process_name="notepad++",
            app_type=ApplicationType.EDITOR,
            preferred_strategies=["clipboard", "keyboard", "ui_automation"],
            key_delay=0.005,
            paste_compatibility="full"
        )
        
        profiles["sublime_text_EDITOR"] = ApplicationProfile(
            name="Sublime Text",
            process_name="sublime_text",
            app_type=ApplicationType.EDITOR,
            preferred_strategies=["clipboard", "keyboard", "ui_automation"],
            key_delay=0.003,
            paste_compatibility="full"
        )
        
        # IDEs
        profiles["devenv_IDE"] = ApplicationProfile(
            name="Visual Studio",
            process_name="devenv",
            app_type=ApplicationType.IDE,
            preferred_strategies=["clipboard", "ui_automation", "keyboard"],
            key_delay=0.005,
            supports_ui_automation=True,
            paste_compatibility="full"
        )
        
        profiles["idea_IDE"] = ApplicationProfile(
            name="IntelliJ IDEA",
            process_name="idea",
            app_type=ApplicationType.IDE,
            preferred_strategies=["clipboard", "ui_automation", "keyboard"],
            key_delay=0.003,
            supports_ui_automation=True,
            paste_compatibility="full"
        )
        
        # Browsers
        profiles["chrome_BROWSER"] = ApplicationProfile(
            name="Google Chrome",
            process_name="chrome",
            app_type=ApplicationType.BROWSER,
            preferred_strategies=["keyboard", "ui_automation", "send_input"],
            key_delay=0.015,
            requires_slow_typing=True,
            injection_delay_ms=100
        )
        
        profiles["firefox_BROWSER"] = ApplicationProfile(
            name="Mozilla Firefox",
            process_name="firefox",
            app_type=ApplicationType.BROWSER,
            preferred_strategies=["keyboard", "ui_automation", "send_input"],
            key_delay=0.012,
            requires_slow_typing=True,
            injection_delay_ms=80
        )
        
        # Terminals
        profiles["cmd_TERMINAL"] = ApplicationProfile(
            name="Command Prompt",
            process_name="cmd",
            app_type=ApplicationType.TERMINAL,
            preferred_strategies=["keyboard", "send_input"],
            key_delay=0.025,
            supports_paste=False,
            requires_slow_typing=True,
            paste_compatibility="none"
        )
        
        profiles["powershell_TERMINAL"] = ApplicationProfile(
            name="PowerShell",
            process_name="powershell",
            app_type=ApplicationType.TERMINAL,
            preferred_strategies=["keyboard", "send_input"],
            key_delay=0.02,
            supports_paste=False,
            requires_slow_typing=True,
            paste_compatibility="limited"
        )
        
        # Office
        profiles["winword_OFFICE"] = ApplicationProfile(
            name="Microsoft Word",
            process_name="winword",
            app_type=ApplicationType.OFFICE,
            preferred_strategies=["ui_automation", "clipboard", "keyboard"],
            key_delay=0.008,
            supports_ui_automation=True,
            paste_compatibility="full"
        )
        
        return profiles
    
    def _create_unknown_app_info(self) -> ApplicationInfo:
        """Create a default ApplicationInfo for unknown applications"""
        return ApplicationInfo(
            name="unknown",
            process_name="unknown",
            window_title="",
            app_type=ApplicationType.UNKNOWN,
            extra_info={"platform": self.platform}
        )
    
    def get_detection_capabilities(self) -> Dict[str, bool]:
        """Get detection capabilities for current platform"""
        capabilities = {
            "can_detect_active_window": False,
            "can_get_process_name": False,
            "can_get_window_title": False,
            "can_get_window_class": False,
            "can_get_process_path": False,
            "supports_caching": True
        }
        
        if self.platform == "Windows":
            capabilities.update({
                "can_detect_active_window": bool(self.windows_modules),
                "can_get_process_name": bool(self.windows_modules),
                "can_get_window_title": bool(self.windows_modules),
                "can_get_window_class": bool(self.windows_modules),
                "can_get_process_path": bool(self.windows_modules)
            })
        elif self.platform == "Linux":
            has_tools = any(self.linux_tools.values())
            capabilities.update({
                "can_detect_active_window": has_tools,
                "can_get_process_name": has_tools,
                "can_get_window_title": has_tools,
                "can_get_window_class": self.linux_tools.get('xdotool', False),
                "can_get_process_path": has_tools
            })
        elif self.platform == "Darwin":
            capabilities.update({
                "can_detect_active_window": True,
                "can_get_process_name": True,
                "can_get_window_title": True,
                "can_get_window_class": False,
                "can_get_process_path": True
            })
        
        return capabilities


# Global detector instance
_detector = None


def get_application_detector() -> EnhancedApplicationDetector:
    """Get global application detector instance"""
    global _detector
    if _detector is None:
        _detector = EnhancedApplicationDetector()
    return _detector


def detect_current_application() -> ApplicationInfo:
    """Convenience function to detect current application"""
    return get_application_detector().detect_active_window()


def get_current_application_profile() -> ApplicationProfile:
    """Convenience function to get current application profile"""
    detector = get_application_detector()
    app_info = detector.detect_active_window()
    return detector.get_application_profile(app_info)