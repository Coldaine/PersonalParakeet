#!/usr/bin/env python3
"""
Text Injector - Cross-platform text injection system for PersonalParakeet v3

Provides unified text injection interface with platform-specific implementations
and fallback mechanisms for reliable text injection across all supported platforms.
"""

import logging
import platform
import time
import threading
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

from .injection_manager_enhanced import EnhancedInjectionManager, InjectionResult
from .application_detector import ApplicationInfo, EnhancedApplicationDetector

logger = logging.getLogger(__name__)


class InjectionMethod(Enum):
    """Available injection methods"""
    PRIMARY = "primary"      # Best available method for current platform
    FALLBACK = "fallback"    # Reliable fallback method
    EMERGENCY = "emergency"  # Last resort method


@dataclass
class InjectionContext:
    """Context for text injection operation"""
    text: str
    method: InjectionMethod
    app_info: Optional[ApplicationInfo] = None
    retry_count: int = 0
    timeout: float = 5.0


class TextInjector:
    """
    Cross-platform text injection system with multiple fallback strategies.
    
    Provides reliable text injection across Windows, Linux, and macOS with
    automatic method selection and error recovery.
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize text injector
        
        Args:
            enabled: Whether injection is active
        """
        self.enabled = enabled
        self.platform = platform.system().lower()
        self._injection_lock = threading.Lock()
        
        # Platform-specific components
        self._enhanced_manager = None
        self._application_detector = None
        self._platform_initialized = False
        
        # Performance tracking
        self._injection_stats = {
            'total_attempts': 0,
            'successful_injections': 0,
            'failed_injections': 0,
            'last_success_time': None,
            'consecutive_failures': 0
        }
        
        logger.info(f"TextInjector initialized (enabled={enabled}, platform={self.platform})")
        
        if self.enabled:
            self._initialize_platform()
    
    def _initialize_platform(self):
        """Initialize platform-specific components"""
        if self._platform_initialized or not self.enabled:
            return
            
        try:
            # Initialize enhanced injection manager
            self._enhanced_manager = EnhancedInjectionManager()
            
            # Initialize application detector
            self._application_detector = EnhancedApplicationDetector()
            
            # Platform-specific initialization
            if self.platform == "windows":
                self._init_windows()
            elif self.platform == "linux":
                self._init_linux()
            elif self.platform == "darwin":
                self._init_macos()
            else:
                logger.warning(f"Unsupported platform for text injection: {self.platform}")
                self.enabled = False
                
            if self.enabled:
                self._platform_initialized = True
                logger.info("Text injector platform initialization completed")
                
        except Exception as e:
            logger.error(f"Failed to initialize text injector: {e}")
            self.enabled = False
    
    def _init_windows(self):
        """Initialize Windows-specific components"""
        try:
            # Enhanced injection manager already handles Windows specifics
            logger.debug("Windows text injection initialized")
        except Exception as e:
            logger.error(f"Windows initialization failed: {e}")
            raise
    
    def _init_linux(self):
        """Initialize Linux-specific components"""
        try:
            # Initialize Linux-specific injection methods
            self._init_linux_x11()
            logger.debug("Linux text injection initialized")
        except Exception as e:
            logger.error(f"Linux initialization failed: {e}")
            raise
    
    def _init_linux_x11(self):
        """Initialize X11-based injection for Linux"""
        try:
            from Xlib import X, display
            import Xlib.ext.xtest as xtest
            
            self._x11_display = display.Display()
            self._xtest = xtest
            logger.debug("X11 injection initialized")
        except ImportError:
            logger.warning("python-xlib not available for Linux injection")
            raise
    
    def _init_macos(self):
        """Initialize macOS-specific components"""
        try:
            # Initialize macOS-specific injection methods
            self._init_macos_quartz()
            logger.debug("macOS text injection initialized")
        except Exception as e:
            logger.error(f"macOS initialization failed: {e}")
            raise
    
    def _init_macos_quartz(self):
        """Initialize Quartz-based injection for macOS"""
        try:
            try:
                from AppKit import NSEvent
                import Quartz
            except ImportError:
                logger.warning("PyObjC frameworks not available for macOS injection")
                raise
            
            self._ns_event = NSEvent
            self._quartz = Quartz
            logger.debug("Quartz injection initialized")
        except ImportError:
            logger.warning("PyObjC frameworks not available for macOS injection")
            raise
    
    def inject_text(self, text: str, method: InjectionMethod = InjectionMethod.PRIMARY,
                   app_info: Optional[ApplicationInfo] = None) -> bool:
        """
        Inject text using the specified method
        
        Args:
            text: Text to inject
            method: Injection method to use
            app_info: Optional application information
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self._platform_initialized:
            logger.warning("Text injector not enabled or not initialized")
            return False
        
        if not text or not text.strip():
            logger.debug("Empty text provided, skipping injection")
            return True  # Empty text is considered successful
        
        # Create injection context
        context = InjectionContext(
            text=text.strip(),
            method=method,
            app_info=app_info or self._get_current_app_info()
        )
        
        # Update statistics
        self._injection_stats['total_attempts'] += 1
        
        # Attempt injection with locking
        with self._injection_lock:
            try:
                success = self._perform_injection(context)
                
                if success:
                    self._injection_stats['successful_injections'] += 1
                    self._injection_stats['last_success_time'] = time.time()
                    self._injection_stats['consecutive_failures'] = 0
                    logger.debug(f"Text injected successfully: {text[:50]}...")
                else:
                    self._injection_stats['failed_injections'] += 1
                    self._injection_stats['consecutive_failures'] += 1
                    logger.warning(f"Text injection failed: {text[:50]}...")
                
                return success
                
            except Exception as e:
                self._injection_stats['failed_injections'] += 1
                self._injection_stats['consecutive_failures'] += 1
                logger.error(f"Text injection error: {e}")
                return False
    
    def _perform_injection(self, context: InjectionContext) -> bool:
        """
        Perform the actual text injection
        
        Args:
            context: Injection context
            
        Returns:
            True if successful, False otherwise
        """
        # Try enhanced injection manager first (best for Windows)
        if self._enhanced_manager and hasattr(self._enhanced_manager, 'inject_text') and self.platform == "windows":
            if self._try_enhanced_injection(context):
                return True
        
        # Platform-specific injection
        if self.platform == "windows":
            return self._inject_windows(context)
        elif self.platform == "linux":
            return self._inject_linux(context)
        elif self.platform == "darwin":
            return self._inject_macos(context)
        
        return False
    
    def _try_enhanced_injection(self, context: InjectionContext) -> bool:
        """Try injection using enhanced injection manager"""
        try:
            if self._enhanced_manager and hasattr(self._enhanced_manager, 'inject_text'):
                result = self._enhanced_manager.inject_text(context.text, context.app_info)
            else:
                result = False
            return result
        except Exception as e:
            logger.debug(f"Enhanced injection failed: {e}")
            return False
    
    def _inject_windows(self, context: InjectionContext) -> bool:
        """Windows-specific text injection"""
        try:
            # Try different methods in order of preference
            
            # Method 1: Enhanced manager (already tried above)
            if self._enhanced_manager:
                try:
                    if self._enhanced_manager.inject_text(context.text, context.app_info):
                        return True
                except:
                    pass
            
            # Method 2: Direct keyboard simulation
            if self._inject_windows_keyboard(context):
                return True
            
            # Method 3: Clipboard fallback
            if self._inject_windows_clipboard(context):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Windows injection failed: {e}")
            return False
    
    def _inject_windows_keyboard(self, context: InjectionContext) -> bool:
        """Windows keyboard-based injection"""
        try:
            import keyboard
            
            # Small delay for focus
            time.sleep(0.01)
            
            # Type the text
            keyboard.write(context.text)
            return True
            
        except ImportError:
            logger.debug("Keyboard library not available")
            return False
        except Exception as e:
            logger.debug(f"Windows keyboard injection failed: {e}")
            return False
    
    def _inject_windows_clipboard(self, context: InjectionContext) -> bool:
        """Windows clipboard-based injection"""
        try:
            import pyperclip
            import keyboard
            
            # Save current clipboard
            original_clipboard = pyperclip.paste()
            
            # Set new text
            pyperclip.copy(context.text)
            
            # Small delay
            time.sleep(0.01)
            
            # Paste
            keyboard.press_and_release('ctrl+v')
            
            # Restore clipboard
            time.sleep(0.01)
            pyperclip.copy(original_clipboard)
            
            return True
            
        except ImportError:
            logger.debug("Clipboard libraries not available")
            return False
        except Exception as e:
            logger.debug(f"Windows clipboard injection failed: {e}")
            return False
    
    def _inject_linux(self, context: InjectionContext) -> bool:
        """Linux-specific text injection"""
        try:
            # Try different methods
            
            # Method 1: X11 keyboard simulation
            if self._inject_linux_x11_keyboard(context):
                return True
            
            # Method 2: Clipboard fallback
            if self._inject_linux_clipboard(context):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Linux injection failed: {e}")
            return False
    
    def _inject_linux_x11_keyboard(self, context: InjectionContext) -> bool:
        """Linux X11 keyboard-based injection"""
        try:
            if not hasattr(self, '_x11_display') or not hasattr(self, '_xtest'):
                return False
            
            # Simple keyboard simulation using XTest
            # This is a basic implementation - in practice, you'd want
            # more sophisticated key mapping and handling
            
            # For now, we'll use a simple approach with external tools
            # if available, or fall back to clipboard
            
            return False  # Placeholder for full implementation
            
        except Exception as e:
            logger.debug(f"Linux X11 keyboard injection failed: {e}")
            return False
    
    def _inject_linux_clipboard(self, context: InjectionContext) -> bool:
        """Linux clipboard-based injection"""
        try:
            import pyperclip
            
            # Try to use xdotool if available
            import subprocess
            
            # Save current clipboard
            original_clipboard = pyperclip.paste()
            
            # Set new text
            pyperclip.copy(context.text)
            
            # Try to paste using xdotool
            try:
                subprocess.run(['xdotool', 'key', 'ctrl+v'], 
                             check=True, timeout=2, capture_output=True)
                
                # Restore clipboard
                time.sleep(0.01)
                pyperclip.copy(original_clipboard)
                
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Fallback: try xclip
            try:
                subprocess.run(['xclip', '-selection', 'clipboard'], 
                             input=context.text.encode(), check=True, timeout=2)
                subprocess.run(['xdotool', 'key', 'ctrl+v'], 
                             check=True, timeout=2, capture_output=True)
                
                # Restore clipboard
                time.sleep(0.01)
                pyperclip.copy(original_clipboard)
                
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            return False
            
        except ImportError:
            logger.debug("Clipboard libraries not available")
            return False
        except Exception as e:
            logger.debug(f"Linux clipboard injection failed: {e}")
            return False
    
    def _inject_macos(self, context: InjectionContext) -> bool:
        """macOS-specific text injection"""
        try:
            # Try different methods
            
            # Method 1: Quartz events
            if self._inject_macos_quartz(context):
                return True
            
            # Method 2: Clipboard fallback
            if self._inject_macos_clipboard(context):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"macOS injection failed: {e}")
            return False
    
    def _inject_macos_quartz(self, context: InjectionContext) -> bool:
        """macOS Quartz-based injection"""
        try:
            if not hasattr(self, '_quartz'):
                return False
            
            # Quartz event-based injection
            # This is a complex implementation that would require
            # detailed key event generation
            
            return False  # Placeholder for full implementation
            
        except Exception as e:
            logger.debug(f"macOS Quartz injection failed: {e}")
            return False
    
    def _inject_macos_clipboard(self, context: InjectionContext) -> bool:
        """macOS clipboard-based injection"""
        try:
            import pyperclip
            import subprocess
            
            # Save current clipboard
            original_clipboard = pyperclip.paste()
            
            # Set new text
            pyperclip.copy(context.text)
            
            # Try to paste using AppleScript
            try:
                applescript = f'tell application "System Events" to keystroke "v" using command down'
                subprocess.run(['osascript', '-e', applescript], 
                             check=True, timeout=2, capture_output=True)
                
                # Restore clipboard
                time.sleep(0.01)
                pyperclip.copy(original_clipboard)
                
                return True
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            return False
            
        except ImportError:
            logger.debug("Clipboard libraries not available")
            return False
        except Exception as e:
            logger.debug(f"macOS clipboard injection failed: {e}")
            return False
    
    def _get_current_app_info(self) -> Optional[ApplicationInfo]:
        """Get current application information"""
        if not self._application_detector:
            return None
            
        try:
            return self._application_detector.detect_current_application()
        except Exception as e:
            logger.debug(f"Failed to get current app info: {e}")
            return None
    
    def get_injection_stats(self) -> Dict[str, Any]:
        """Get injection statistics"""
        return self._injection_stats.copy()
    
    def reset_stats(self):
        """Reset injection statistics"""
        self._injection_stats = {
            'total_attempts': 0,
            'successful_injections': 0,
            'failed_injections': 0,
            'last_success_time': None,
            'consecutive_failures': 0
        }
        logger.debug("Injection statistics reset")
    
    def is_enabled(self) -> bool:
        """Check if injector is enabled"""
        return self.enabled and self._platform_initialized
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the injector"""
        self.enabled = enabled
        if enabled and not self._platform_initialized:
            self._initialize_platform()
        logger.info(f"Text injector {'enabled' if enabled else 'disabled'}")


def create_text_injector(enabled: bool = True) -> TextInjector:
    """Factory function to create a text injector"""
    return TextInjector(enabled=enabled)
