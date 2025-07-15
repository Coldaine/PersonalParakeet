"""Platform-aware text injection strategies for PersonalParakeet

This module provides intelligent text injection strategies that adapt to different
platforms (Windows, Linux, macOS) and applications (editors, browsers, terminals).
"""

import platform
import os
import sys
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Dict, Any, Callable
import time
from abc import ABC, abstractmethod
from .logger import setup_logger
from .config import InjectionConfig

logger = setup_logger(__name__)


class Platform(Enum):
    """Supported platforms"""
    WINDOWS = auto()
    LINUX = auto()
    MACOS = auto()
    UNKNOWN = auto()


class DesktopEnvironment(Enum):
    """Desktop environments (mainly for Linux)"""
    WINDOWS_DESKTOP = auto()
    KDE = auto()
    GNOME = auto()
    XFCE = auto()
    X11_GENERIC = auto()
    WAYLAND = auto()
    MACOS_AQUA = auto()
    UNKNOWN = auto()


class SessionType(Enum):
    """Session types for Linux"""
    X11 = auto()
    WAYLAND = auto()
    WINDOWS = auto()
    MACOS = auto()
    UNKNOWN = auto()


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
class PlatformInfo:
    """Complete platform information"""
    platform: Platform
    desktop_env: DesktopEnvironment
    session_type: SessionType
    version: str
    extra_info: Dict[str, Any]


@dataclass
class ApplicationInfo:
    """Information about the active application"""
    name: str
    process_name: str
    window_title: str
    app_type: ApplicationType
    window_class: Optional[str] = None
    extra_info: Optional[Dict[str, Any]] = None


class PlatformDetector:
    """Detects platform, desktop environment, and session type"""
    
    _cached_info: Optional[PlatformInfo] = None
    
    @classmethod
    def detect(cls, force_refresh: bool = False) -> PlatformInfo:
        """Detect platform information with caching"""
        if cls._cached_info and not force_refresh:
            return cls._cached_info
            
        system = platform.system().lower()
        
        if system == "windows":
            info = cls._detect_windows()
        elif system == "linux":
            info = cls._detect_linux()
        elif system == "darwin":
            info = cls._detect_macos()
        else:
            info = PlatformInfo(
                platform=Platform.UNKNOWN,
                desktop_env=DesktopEnvironment.UNKNOWN,
                session_type=SessionType.UNKNOWN,
                version=platform.version(),
                extra_info={}
            )
        
        cls._cached_info = info
        return info
    
    @classmethod
    def _detect_windows(cls) -> PlatformInfo:
        """Detect Windows platform details"""
        import sys
        
        version_info = sys.getwindowsversion()
        
        return PlatformInfo(
            platform=Platform.WINDOWS,
            desktop_env=DesktopEnvironment.WINDOWS_DESKTOP,
            session_type=SessionType.WINDOWS,
            version=f"{version_info.major}.{version_info.minor}.{version_info.build}",
            extra_info={
                "edition": platform.win32_edition() if hasattr(platform, 'win32_edition') else "Unknown",
                "machine": platform.machine(),
                "processor": platform.processor()
            }
        )
    
    @classmethod
    def _detect_linux(cls) -> PlatformInfo:
        """Detect Linux platform details including desktop environment"""
        # Detect desktop environment
        desktop_env = DesktopEnvironment.UNKNOWN
        session_type = SessionType.UNKNOWN
        
        # Check environment variables
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        session = os.environ.get('XDG_SESSION_TYPE', '').lower()
        
        # Detect session type
        if session == 'x11':
            session_type = SessionType.X11
        elif session == 'wayland':
            session_type = SessionType.WAYLAND
        elif os.environ.get('DISPLAY'):
            session_type = SessionType.X11
        elif os.environ.get('WAYLAND_DISPLAY'):
            session_type = SessionType.WAYLAND
        
        # Detect desktop environment
        if 'kde' in desktop or 'plasma' in desktop:
            desktop_env = DesktopEnvironment.KDE
        elif 'gnome' in desktop:
            desktop_env = DesktopEnvironment.GNOME
        elif 'xfce' in desktop:
            desktop_env = DesktopEnvironment.XFCE
        elif session_type == SessionType.X11:
            desktop_env = DesktopEnvironment.X11_GENERIC
        elif session_type == SessionType.WAYLAND:
            desktop_env = DesktopEnvironment.WAYLAND
        
        # Get distribution info
        try:
            import distro
            dist_name = distro.name()
            dist_version = distro.version()
        except ImportError:
            dist_name = "Unknown"
            dist_version = platform.release()
        
        return PlatformInfo(
            platform=Platform.LINUX,
            desktop_env=desktop_env,
            session_type=session_type,
            version=dist_version,
            extra_info={
                "distribution": dist_name,
                "kernel": platform.release(),
                "desktop_session": os.environ.get('DESKTOP_SESSION', 'Unknown')
            }
        )
    
    @classmethod
    def _detect_macos(cls) -> PlatformInfo:
        """Detect macOS platform details"""
        return PlatformInfo(
            platform=Platform.MACOS,
            desktop_env=DesktopEnvironment.MACOS_AQUA,
            session_type=SessionType.MACOS,
            version=platform.mac_ver()[0],
            extra_info={
                "machine": platform.machine(),
                "processor": platform.processor()
            }
        )


class TextInjectionStrategy(ABC):
    """Abstract base class for text injection strategies"""
    
    def __init__(self):
        self.fallback_callback: Optional[Callable[[str], None]] = None
    
    @abstractmethod
    def inject(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text into the active application
        
        Args:
            text: Text to inject
            app_info: Optional information about the target application
            
        Returns:
            True if injection succeeded, False otherwise
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if this injection method is available on the system"""
        pass
    
    def set_fallback(self, callback: Callable[[str], None]):
        """Set a fallback callback for when injection fails"""
        self.fallback_callback = callback


class TextInjectionManager:
    """Manages text injection across different platforms and applications"""
    
    def __init__(self, config: Optional[InjectionConfig] = None):
        self.config = config if config is not None else InjectionConfig()
        self.platform_info = PlatformDetector.detect()
        self.strategies: Dict[str, TextInjectionStrategy] = {}
        self.fallback_display: Optional[Callable[[str], None]] = None
        self.app_detector = None
        self._initialize_app_detector()
        self._initialize_strategies()
    
    def _initialize_app_detector(self):
        """Initialize application detector"""
        try:
            from .application_detection import ApplicationDetector
            self.app_detector = ApplicationDetector()
        except ImportError as e:
            logger.warning(f"Application detection not available: {e}")
    
    def _initialize_strategies(self):
        """Initialize platform-specific injection strategies"""
        if self.platform_info.platform == Platform.WINDOWS:
            # Import Windows-specific strategies dynamically
            try:
                from .windows_injection import (
                    WindowsUIAutomationStrategy,
                    WindowsKeyboardStrategy,
                    WindowsClipboardStrategy
                )
                self.strategies['ui_automation'] = WindowsUIAutomationStrategy(self.config)
                self.strategies['keyboard'] = WindowsKeyboardStrategy(self.config)
                self.strategies['clipboard'] = WindowsClipboardStrategy(self.config)
            except ImportError as e:
                logger.error(f"Failed to import Windows strategies: {e}")
                
        elif self.platform_info.platform == Platform.LINUX:
            # Import Linux-specific strategies dynamically
            try:
                from .linux_injection import (
                    LinuxXTestStrategy,
                    LinuxXdotoolStrategy,
                    LinuxATSPIStrategy,
                    LinuxClipboardStrategy
                )
                
                # For KDE, use the optimized simple injector
                if self.platform_info.desktop_env == DesktopEnvironment.KDE:
                    try:
                        from .kde_injection import KDESimpleInjector
                        self.strategies['kde_simple'] = KDESimpleInjector(self.config)
                    except ImportError:
                        pass
                
                if self.platform_info.session_type == SessionType.X11:
                    self.strategies['xtest'] = LinuxXTestStrategy(self.config)
                    self.strategies['xdotool'] = LinuxXdotoolStrategy(self.config)
                elif self.platform_info.session_type == SessionType.WAYLAND:
                    self.strategies['atspi'] = LinuxATSPIStrategy(self.config)
                    
                self.strategies['clipboard'] = LinuxClipboardStrategy(self.config)
            except ImportError as e:
                logger.error(f"Failed to import Linux strategies: {e}")
        
        # Always add the basic keyboard strategy as fallback
        try:
            import keyboard
            from .basic_injection import BasicKeyboardStrategy
            self.strategies['basic_keyboard'] = BasicKeyboardStrategy()
        except ImportError:
            logger.warning("keyboard module not available")
    
    def inject_text(self, text: str, app_info: Optional[ApplicationInfo] = None) -> bool:
        """Inject text using the best available strategy.
        
        This method automatically selects the optimal injection strategy based on
        the current platform and target application. It implements a fallback chain
        to ensure text is injected even if the preferred method fails.
        
        Args:
            text: The text to inject into the active application
            app_info: Optional information about the target application. If not
                     provided, will attempt to auto-detect the active window.
        
        Returns:
            bool: True if injection succeeded, False if all strategies failed
            
        Raises:
            None: All exceptions are caught and logged. Failures result in
                  fallback attempts rather than exceptions.
                  
        Example:
            >>> injector = TextInjectionManager()
            >>> success = injector.inject_text("Hello, World!")
            >>> if not success:
            ...     print("All injection strategies failed")
        
        Note:
            The method adds a trailing space to the injected text to ensure
            proper word separation in continuous dictation scenarios.
        """
        # Auto-detect application if not provided
        if not app_info and self.app_detector:
            try:
                app_info = self.app_detector.detect_active_window()
                logger.info(f"Detected application: {app_info.name} ({app_info.app_type.name})")
            except Exception as e:
                logger.warning(f"Application detection failed: {e}")
        
        # Select strategies based on platform and application
        strategy_order = self._get_strategy_order(app_info)
        
        for strategy_name in strategy_order:
            if strategy_name in self.strategies:
                strategy = self.strategies[strategy_name]
                if strategy.is_available():
                    try:
                        logger.debug(f"Trying {strategy_name} strategy...")
                        if strategy.inject(text, app_info):
                            logger.info(f"Successfully injected text using {strategy_name}")
                            return True
                    except Exception as e:
                        logger.error(f"Strategy {strategy_name} failed: {e}")
        
        # All strategies failed - use fallback display
        if self.fallback_display:
            logger.warning("All injection strategies failed, using fallback display")
            self.fallback_display(text)
        
        return False
    
    def _get_strategy_order(self, app_info: Optional[ApplicationInfo]) -> list:
        """Determine optimal strategy order based on platform and application"""
        if self.platform_info.platform == Platform.WINDOWS:
            return self._get_windows_strategy_order(app_info)
        elif self.platform_info.platform == Platform.LINUX:
            return self._get_linux_strategy_order(app_info)
        else:
            return ['basic_keyboard']

    def _get_windows_strategy_order(self, app_info: Optional[ApplicationInfo]) -> list:
        """Get Windows-specific strategy order"""
        if not app_info:
            return ['ui_automation', 'keyboard', 'clipboard', 'basic_keyboard']
            
        # Application-specific optimizations
        strategies_by_app = {
            ApplicationType.EDITOR: ['clipboard', 'ui_automation', 'keyboard', 'basic_keyboard'],
            ApplicationType.IDE: ['clipboard', 'ui_automation', 'keyboard', 'basic_keyboard'],
            ApplicationType.TERMINAL: ['ui_automation', 'keyboard', 'basic_keyboard'],
            ApplicationType.BROWSER: ['keyboard', 'ui_automation', 'basic_keyboard'],
        }
        
        return strategies_by_app.get(
            app_info.app_type, 
            ['ui_automation', 'keyboard', 'clipboard', 'basic_keyboard']
        )

    def _get_linux_strategy_order(self, app_info: Optional[ApplicationInfo]) -> list:
        """Get Linux-specific strategy order"""
        if self.platform_info.desktop_env == DesktopEnvironment.KDE:
            return self._get_kde_strategy_order(app_info)
        elif self.platform_info.session_type == SessionType.X11:
            return self._get_x11_strategy_order(app_info)
        else:  # Wayland
            return ['atspi', 'clipboard', 'basic_keyboard']

    def _get_kde_strategy_order(self, app_info: Optional[ApplicationInfo]) -> list:
        """Get KDE-specific strategy order"""
        if app_info and app_info.app_type in (ApplicationType.EDITOR, ApplicationType.IDE):
            return ['clipboard', 'kde_simple', 'xtest', 'xdotool', 'basic_keyboard']
        return ['kde_simple', 'xtest', 'xdotool', 'clipboard', 'basic_keyboard']

    def _get_x11_strategy_order(self, app_info: Optional[ApplicationInfo]) -> list:
        """Get X11-specific strategy order"""
        if app_info and app_info.app_type in (ApplicationType.EDITOR, ApplicationType.IDE):
            return ['clipboard', 'xtest', 'xdotool', 'basic_keyboard']
        return ['xtest', 'xdotool', 'clipboard', 'basic_keyboard']
    
    def set_fallback_display(self, callback: Callable[[str], None]):
        """Set fallback display callback for when all injection methods fail"""
        self.fallback_display = callback
    
    def get_platform_info(self) -> PlatformInfo:
        """Get detected platform information"""
        return self.platform_info