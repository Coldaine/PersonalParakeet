"""
Wayland text injection implementation using multiple fallback strategies.
This module tries various methods to inject text on Wayland systems.
"""

import os
import subprocess
import shutil
import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class WaylandCompositor(Enum):
    """Known Wayland compositors."""
    UNKNOWN = "unknown"
    GNOME = "gnome"  # Mutter
    KDE = "kde"      # KWin
    SWAY = "sway"    # wlroots
    WESTON = "weston"
    HYPRLAND = "hyprland"  # wlroots
    RIVER = "river"  # wlroots
    WAYFIRE = "wayfire"  # wlroots


class InjectionMethod(Enum):
    """Available injection methods for Wayland."""
    VIRTUAL_KB = "virtual_keyboard"  # Native Wayland virtual keyboard protocol
    WTYPE = "wtype"
    YDOTOOL = "ydotool"
    CLIPBOARD = "clipboard"
    XWAYLAND = "xwayland"
    UINPUT = "uinput"
    NONE = "none"


@dataclass
class WaylandCapabilities:
    """Detected Wayland capabilities."""
    compositor: WaylandCompositor
    available_methods: List[InjectionMethod]
    has_xwayland: bool
    session_type: str  # wayland or x11
    has_virtual_keyboard: bool = False  # Native virtual keyboard protocol support
    

class WaylandInjector:
    """Handles text injection on Wayland systems with multiple fallback methods."""
    
    def __init__(self):
        self.capabilities = self._detect_capabilities()
        self.method_priority = self._determine_method_priority()
        self._ydotool_daemon_checked = False
        self._needs_sudo = False
        self._virtual_keyboard_injector = None  # Lazy initialization
        
    def _detect_capabilities(self) -> WaylandCapabilities:
        """Detect Wayland environment and available injection methods."""
        # Check session type
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        wayland_display = os.environ.get('WAYLAND_DISPLAY', '')
        
        # Detect compositor
        compositor = self._detect_compositor()
        
        # Check available tools
        available_methods = []
        
        # Check for virtual keyboard protocol (highest priority)
        has_virtual_keyboard = self._check_virtual_keyboard_support()
        if has_virtual_keyboard:
            available_methods.append(InjectionMethod.VIRTUAL_KB)
        
        # Check for wtype (wlroots compositors)
        if shutil.which('wtype') and compositor in [
            WaylandCompositor.SWAY, WaylandCompositor.HYPRLAND, 
            WaylandCompositor.RIVER, WaylandCompositor.WAYFIRE
        ]:
            available_methods.append(InjectionMethod.WTYPE)
            
        # Check for ydotool
        if shutil.which('ydotool'):
            available_methods.append(InjectionMethod.YDOTOOL)
            
        # Check for clipboard tools
        if shutil.which('wl-copy') and shutil.which('wl-paste'):
            available_methods.append(InjectionMethod.CLIPBOARD)
            
        # Check XWayland
        has_xwayland = bool(os.environ.get('DISPLAY'))
        if has_xwayland:
            available_methods.append(InjectionMethod.XWAYLAND)
            
        # Check if we can access uinput (requires permissions)
        if os.path.exists('/dev/uinput'):
            try:
                # Try to open it (will fail without permissions)
                with open('/dev/uinput', 'rb'):
                    available_methods.append(InjectionMethod.UINPUT)
            except (IOError, OSError):
                pass
                
        return WaylandCapabilities(
            compositor=compositor,
            available_methods=available_methods,
            has_xwayland=has_xwayland,
            session_type=session_type,
            has_virtual_keyboard=has_virtual_keyboard
        )
        
    def _detect_compositor(self) -> WaylandCompositor:
        """Detect which Wayland compositor is running."""
        # Check environment variables
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        session = os.environ.get('DESKTOP_SESSION', '').lower()
        
        # Check various indicators
        checks = [
            ('gnome' in desktop or 'gnome' in session, WaylandCompositor.GNOME),
            ('kde' in desktop or 'plasma' in desktop, WaylandCompositor.KDE),
            ('sway' in desktop or 'sway' in session, WaylandCompositor.SWAY),
            ('hyprland' in desktop, WaylandCompositor.HYPRLAND),
            ('river' in desktop, WaylandCompositor.RIVER),
            ('wayfire' in desktop, WaylandCompositor.WAYFIRE),
            ('weston' in desktop, WaylandCompositor.WESTON),
        ]
        
        for condition, compositor in checks:
            if condition:
                return compositor
                
        # Try process detection
        try:
            ps_output = subprocess.check_output(['ps', 'aux'], text=True)
            process_checks = [
                ('gnome-shell', WaylandCompositor.GNOME),
                ('kwin_wayland', WaylandCompositor.KDE),
                ('sway', WaylandCompositor.SWAY),
                ('Hyprland', WaylandCompositor.HYPRLAND),
                ('river', WaylandCompositor.RIVER),
                ('wayfire', WaylandCompositor.WAYFIRE),
            ]
            
            for process, compositor in process_checks:
                if process in ps_output:
                    return compositor
        except:
            pass
            
        return WaylandCompositor.UNKNOWN
    
    def _check_virtual_keyboard_support(self) -> bool:
        """Check if virtual keyboard protocol is supported."""
        try:
            # Only check if we're on Wayland
            if os.environ.get('XDG_SESSION_TYPE') != 'wayland':
                return False
            
            if not os.environ.get('WAYLAND_DISPLAY'):
                return False
            
            # Try to import and check availability
            from .virtual_keyboard_injector import VirtualKeyboardInjector
            injector = VirtualKeyboardInjector()
            return injector.is_available()
            
        except Exception as e:
            logger.debug(f"Virtual keyboard protocol not available: {e}")
            return False
        
    def _determine_method_priority(self) -> List[InjectionMethod]:
        """Determine the priority order for injection methods based on compositor."""
        base_priority = []
        
        # Virtual keyboard protocol gets highest priority (native, fast, no deps)
        if InjectionMethod.VIRTUAL_KB in self.capabilities.available_methods:
            base_priority.append(InjectionMethod.VIRTUAL_KB)
        
        # Compositor-specific preferences
        if self.capabilities.compositor in [
            WaylandCompositor.SWAY, WaylandCompositor.HYPRLAND,
            WaylandCompositor.RIVER, WaylandCompositor.WAYFIRE
        ]:
            # wlroots-based compositors work well with wtype
            base_priority = [
                InjectionMethod.WTYPE,
                InjectionMethod.YDOTOOL,
                InjectionMethod.CLIPBOARD,
                InjectionMethod.XWAYLAND
            ]
        else:
            # GNOME/KDE and others
            base_priority = [
                InjectionMethod.YDOTOOL,
                InjectionMethod.CLIPBOARD,
                InjectionMethod.XWAYLAND,
                InjectionMethod.WTYPE
            ]
            
        # Add uinput if available (powerful but requires permissions)
        if InjectionMethod.UINPUT in self.capabilities.available_methods:
            base_priority.insert(1, InjectionMethod.UINPUT)
            
        # Filter to only available methods
        return [m for m in base_priority if m in self.capabilities.available_methods]
        
    def _ensure_ydotool_daemon(self) -> bool:
        """Ensure ydotool is available (with or without daemon)."""
        if self._ydotool_daemon_checked:
            return True
            
        try:
            # Test if ydotool works (might need sudo)
            result = subprocess.run(['ydotool', 'type', ''], capture_output=True, timeout=1)
            if result.returncode == 0:
                self._ydotool_daemon_checked = True
                return True
                
            # Try with sudo if regular failed
            result = subprocess.run(['sudo', '-n', 'ydotool', 'type', ''], capture_output=True, timeout=1)
            if result.returncode == 0:
                self._ydotool_daemon_checked = True
                self._needs_sudo = True  # Remember we need sudo
                return True
                
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass
            
        # Try to start daemon if ydotoold exists
        try:
            subprocess.Popen(['ydotoold'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import time
            time.sleep(0.5)  # Give daemon time to start
            self._ydotool_daemon_checked = True
            return True
        except:
            pass
            
        return False
                
    def inject_text(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Attempt to inject text using available methods.
        Returns (success, error_message).
        """
        errors = []
        
        for method in self.method_priority:
            try:
                if method == InjectionMethod.VIRTUAL_KB:
                    success, error = self._inject_virtual_keyboard(text)
                elif method == InjectionMethod.WTYPE:
                    success, error = self._inject_wtype(text)
                elif method == InjectionMethod.YDOTOOL:
                    success, error = self._inject_ydotool(text)
                elif method == InjectionMethod.CLIPBOARD:
                    success, error = self._inject_clipboard(text)
                elif method == InjectionMethod.XWAYLAND:
                    success, error = self._inject_xwayland(text)
                elif method == InjectionMethod.UINPUT:
                    success, error = self._inject_uinput(text)
                else:
                    continue
                    
                if success:
                    logger.info(f"Successfully injected text using {method.value}")
                    return True, None
                else:
                    errors.append(f"{method.value}: {error}")
                    
            except Exception as e:
                errors.append(f"{method.value}: {str(e)}")
                
        # All methods failed - try unsafe mode
        try:
            from .wayland_injector_unsafe import UnsafeWaylandInjector
            unsafe = UnsafeWaylandInjector()
            success, error = unsafe.inject_text(text)
            if success:
                logger.warning("Text injected using UNSAFE mode")
                return True, None
            errors.append(f"unsafe mode: {error}")
        except Exception as e:
            errors.append(f"unsafe mode: {str(e)}")
            
        error_msg = "All injection methods failed:\n" + "\n".join(errors)
        return False, error_msg
    
    def _inject_virtual_keyboard(self, text: str) -> Tuple[bool, Optional[str]]:
        """Inject text using native Wayland virtual keyboard protocol."""
        try:
            # Lazy initialization of virtual keyboard injector
            if not self._virtual_keyboard_injector:
                from .virtual_keyboard_injector import VirtualKeyboardInjector
                self._virtual_keyboard_injector = VirtualKeyboardInjector()
            
            # Use the high-performance virtual keyboard protocol
            return self._virtual_keyboard_injector.inject_text(text)
            
        except Exception as e:
            return False, str(e)
        
    def _inject_wtype(self, text: str) -> Tuple[bool, Optional[str]]:
        """Inject text using wtype."""
        try:
            # Escape special characters for shell
            escaped_text = text.replace("'", "'\"'\"'")
            result = subprocess.run(
                ['wtype', escaped_text],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return True, None
            else:
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "wtype command timed out"
        except Exception as e:
            return False, str(e)
            
    def _inject_ydotool(self, text: str) -> Tuple[bool, Optional[str]]:
        """Inject text using ydotool."""
        # Ensure ydotool is available
        if not self._ensure_ydotool_daemon():
            return False, "ydotool not available"
            
        try:
            # Build command based on whether we need sudo
            if hasattr(self, '_needs_sudo') and self._needs_sudo:
                cmd = ['sudo', '-n', 'ydotool', 'type', text]
            else:
                cmd = ['ydotool', 'type', text]
                
            # Run ydotool type command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return True, None
            else:
                # If regular ydotool failed, try with sudo
                if not self._needs_sudo and 'Permission denied' in result.stderr:
                    result = subprocess.run(
                        ['sudo', '-n', 'ydotool', 'type', text],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        self._needs_sudo = True
                        return True, None
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "ydotool command timed out"
        except Exception as e:
            return False, str(e)
            
    def _inject_clipboard(self, text: str) -> Tuple[bool, Optional[str]]:
        """Inject text using clipboard + paste simulation."""
        try:
            # Copy to clipboard
            proc = subprocess.Popen(
                ['wl-copy'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            _, stderr = proc.communicate(input=text, timeout=2)
            
            if proc.returncode != 0:
                return False, f"wl-copy failed: {stderr}"
                
            # Small delay
            import time
            time.sleep(0.1)
            
            # Try to paste using available method
            if InjectionMethod.WTYPE in self.capabilities.available_methods:
                # Use wtype to send Ctrl+V
                result = subprocess.run(
                    ['wtype', '-M', 'ctrl', '-k', 'v'],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    return True, None
                    
            if InjectionMethod.YDOTOOL in self.capabilities.available_methods:
                # Use ydotool to send Ctrl+V
                if self._ensure_ydotool_daemon():
                    result = subprocess.run(
                        ['ydotool', 'key', 'ctrl+v'],
                        capture_output=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        return True, None
                        
            return False, "Could not simulate paste command"
            
        except subprocess.TimeoutExpired:
            return False, "Clipboard operation timed out"
        except Exception as e:
            return False, str(e)
            
    def _inject_xwayland(self, text: str) -> Tuple[bool, Optional[str]]:
        """Try to inject via XWayland if the focused window is an X11 app."""
        # This would need to check if the current window is XWayland
        # and then use X11 injection methods
        # For now, this is a placeholder
        return False, "XWayland injection not implemented yet"
        
    def _inject_uinput(self, text: str) -> Tuple[bool, Optional[str]]:
        """Inject text using uinput (requires permissions)."""
        # This would require python-evdev and proper permissions
        # For now, this is a placeholder
        return False, "uinput injection not implemented yet"
        
    def get_setup_instructions(self) -> str:
        """Get setup instructions for the user."""
        instructions = ["# Wayland Text Injection Setup\n"]
        
        if self.capabilities.session_type != 'wayland':
            instructions.append("You're not running a Wayland session. These instructions are for Wayland.\n")
            
        instructions.append(f"Detected compositor: {self.capabilities.compositor.value}\n")
        instructions.append(f"Available methods: {[m.value for m in self.capabilities.available_methods]}\n")
        
        # Method-specific instructions
        if InjectionMethod.YDOTOOL not in self.capabilities.available_methods:
            instructions.append("\n## Install ydotool (recommended):")
            instructions.append("```bash")
            instructions.append("sudo apt install ydotool  # or your package manager")
            instructions.append("sudo usermod -a -G input $USER")
            instructions.append("# Logout and login again for group changes")
            instructions.append("# Then start the daemon:")
            instructions.append("ydotoold &")
            instructions.append("```")
            
        if self.capabilities.compositor in [WaylandCompositor.SWAY, WaylandCompositor.HYPRLAND] and \
           InjectionMethod.WTYPE not in self.capabilities.available_methods:
            instructions.append("\n## Install wtype (for wlroots compositors):")
            instructions.append("```bash")
            instructions.append("sudo apt install wtype  # or build from source")
            instructions.append("```")
            
        if InjectionMethod.CLIPBOARD not in self.capabilities.available_methods:
            instructions.append("\n## Install wl-clipboard:")
            instructions.append("```bash")
            instructions.append("sudo apt install wl-clipboard")
            instructions.append("```")
            
        return "\n".join(instructions)