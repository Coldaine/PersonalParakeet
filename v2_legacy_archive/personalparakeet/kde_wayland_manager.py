import asyncio
import json
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union

try:
    from dbus_next.aio import MessageBus
    from dbus_next import DBusError
    HAS_DBUS = True
except ImportError:
    HAS_DBUS = False

logger = logging.getLogger(__name__)


class TextInjectionMethod(Enum):
    KDOTOOL = "kdotool"
    DBUS_VIRTUAL_KEYBOARD = "dbus_vkbd"
    YDOTOOL = "ydotool"
    CLIPBOARD = "clipboard"


@dataclass
class WindowInfo:
    """Active window information"""
    title: str
    window_class: str
    window_id: Optional[int] = None
    pid: Optional[int] = None


class KDEWaylandManager:
    """Manages window detection and text injection on KDE Wayland"""
    
    def __init__(self, async_mode: bool = False):
        self.async_mode = async_mode
        self.loop = asyncio.new_event_loop() if async_mode else None
        self.bus = None
        self.available_methods = self._detect_available_methods()
        
        if not self.available_methods:
            raise RuntimeError("No text injection methods available")
    
    def _detect_available_methods(self) -> List[TextInjectionMethod]:
        """Detect which text injection methods are available"""
        methods = []
        
        if shutil.which('kdotool'):
            methods.append(TextInjectionMethod.KDOTOOL)
        
        if HAS_DBUS and self._check_kde_session():
            methods.append(TextInjectionMethod.DBUS_VIRTUAL_KEYBOARD)
        
        if shutil.which('ydotool') and self._check_ydotool_daemon():
            methods.append(TextInjectionMethod.YDOTOOL)
        
        if shutil.which('wl-copy') and shutil.which('wl-paste'):
            methods.append(TextInjectionMethod.CLIPBOARD)
        
        logger.info(f"Available methods: {[m.value for m in methods]}")
        return methods
    
    def _check_kde_session(self) -> bool:
        """Check if running in KDE session"""
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '')
        session_type = os.environ.get('XDG_SESSION_TYPE', '')
        return 'KDE' in desktop and session_type == 'wayland'
    
    def _check_ydotool_daemon(self) -> bool:
        """Check if ydotool daemon is running"""
        try:
            result = subprocess.run(['pgrep', 'ydotoold'], 
                                  capture_output=True)
            return result.returncode == 0
        except:
            return False
    
    def _sanitize_for_kwin_js(self, text: str) -> str:
        """Safely prepare text for KWin JavaScript injection"""
        # Use JSON encoding for safety
        return json.dumps(text)
    
    # === Window Detection Methods ===
    
    def get_active_window(self) -> Optional[WindowInfo]:
        """Get active window info (sync API)"""
        if self.async_mode:
            return self.loop.run_until_complete(self.get_active_window_async())
        
        # Try kdotool first
        if TextInjectionMethod.KDOTOOL in self.available_methods:
            info = self._get_active_window_kdotool()
            if info:
                return info
        
        # Try D-Bus fallback
        if TextInjectionMethod.DBUS_VIRTUAL_KEYBOARD in self.available_methods:
            return asyncio.run(self._get_active_window_dbus())
        
        return None
    
    async def get_active_window_async(self) -> Optional[WindowInfo]:
        """Get active window info (async API)"""
        # Try kdotool first
        if TextInjectionMethod.KDOTOOL in self.available_methods:
            loop = asyncio.get_running_loop()
            info = await loop.run_in_executor(None, self._get_active_window_kdotool)
            if info:
                return info
        
        # Try D-Bus fallback
        if TextInjectionMethod.DBUS_VIRTUAL_KEYBOARD in self.available_methods:
            return await self._get_active_window_dbus()
        
        return None
    
    def _get_active_window_kdotool(self) -> Optional[WindowInfo]:
        """Get active window using kdotool"""
        try:
            # Get window ID
            result = subprocess.run(['kdotool', 'getactivewindow'], 
                                  capture_output=True, text=True, check=True)
            window_id = result.stdout.strip()
            
            # Get window name
            result = subprocess.run(['kdotool', 'getwindowname', window_id],
                                  capture_output=True, text=True, check=True)
            title = result.stdout.strip()
            
            # Get window class
            result = subprocess.run(['kdotool', 'getwindowclassname', window_id],
                                  capture_output=True, text=True, check=True)
            window_class = result.stdout.strip()
            
            return WindowInfo(
                title=title,
                window_class=window_class,
                window_id=int(window_id) if window_id.isdigit() else None
            )
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"kdotool failed: {e}")
            return None
    
    async def _get_active_window_dbus(self) -> Optional[WindowInfo]:
        """Get active window using D-Bus"""
        try:
            if not self.bus:
                self.bus = await MessageBus().connect()
            
            # Get KWin object
            introspection = await self.bus.introspect('org.kde.KWin', '/KWin')
            proxy = self.bus.get_proxy_object('org.kde.KWin', '/KWin', introspection)
            kwin = proxy.get_interface('org.kde.KWin')
            
            # Get active window ID
            window_id = await kwin.call_activeWindow()
            
            if window_id <= 0:
                return None
            
            # Get window properties
            # Note: This part may need adjustment based on KDE version
            return WindowInfo(
                title="Unknown (D-Bus)",
                window_class="Unknown",
                window_id=window_id
            )
            
        except Exception as e:
            logger.error(f"D-Bus window detection failed: {e}")
            return None
    
    # === Text Injection Methods ===
    
    def inject_text(self, text: str) -> bool:
        """Inject text (sync API)"""
        if self.async_mode:
            return self.loop.run_until_complete(self.inject_text_async(text))
        
        # Try methods in order of preference
        for method in self.available_methods:
            try:
                if method == TextInjectionMethod.KDOTOOL:
                    if self._inject_text_kdotool(text):
                        return True
                elif method == TextInjectionMethod.DBUS_VIRTUAL_KEYBOARD:
                    if asyncio.run(self._inject_text_dbus(text)):
                        return True
                elif method == TextInjectionMethod.YDOTOOL:
                    if self._inject_text_ydotool(text):
                        return True
                elif method == TextInjectionMethod.CLIPBOARD:
                    if self._inject_text_clipboard(text):
                        return True
            except Exception as e:
                logger.warning(f"Method {method.value} failed: {e}")
                continue
        
        return False
    
    async def inject_text_async(self, text: str) -> bool:
        """Inject text (async API)"""
        loop = asyncio.get_running_loop()
        
        # Try methods in order of preference
        for method in self.available_methods:
            try:
                if method == TextInjectionMethod.KDOTOOL:
                    if await loop.run_in_executor(None, self._inject_text_kdotool, text):
                        return True
                elif method == TextInjectionMethod.DBUS_VIRTUAL_KEYBOARD:
                    if await self._inject_text_dbus(text):
                        return True
                elif method == TextInjectionMethod.YDOTOOL:
                    if await loop.run_in_executor(None, self._inject_text_ydotool, text):
                        return True
                elif method == TextInjectionMethod.CLIPBOARD:
                    if await loop.run_in_executor(None, self._inject_text_clipboard, text):
                        return True
            except Exception as e:
                logger.warning(f"Method {method.value} failed: {e}")
                continue
        
        return False
    
    def _inject_text_kdotool(self, text: str) -> bool:
        """Inject text using kdotool"""
        try:
            subprocess.run(['kdotool', 'type', text], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"kdotool injection failed: {e}")
            return False
    
    async def _inject_text_dbus(self, text: str) -> bool:
        """Inject text using D-Bus virtual keyboard"""
        script_id = None
        try:
            if not self.bus:
                self.bus = await MessageBus().connect()
            
            # Sanitize text for JavaScript
            safe_text = self._sanitize_for_kwin_js(text)
            js_script = f"workspace.virtualKeyboard.typeText({safe_text});"
            
            # Get scripting interface
            introspection = await self.bus.introspect('org.kde.KWin', '/Scripting')
            proxy = self.bus.get_proxy_object('org.kde.KWin', '/Scripting', introspection)
            scripting = proxy.get_interface('org.kde.kwin.Scripting')
            
            # Load and run script
            script_id = await scripting.call_loadScript(js_script, "TextInjection")
            await scripting.call_run(script_id)
            
            # Give it a moment to execute
            await asyncio.sleep(0.05)
            
            return True
            
        except Exception as e:
            logger.error(f"D-Bus injection failed: {e}")
            return False
        finally:
            if script_id is not None:
                try:
                    await scripting.call_unload(script_id)
                except:
                    pass
    
    def _inject_text_ydotool(self, text: str) -> bool:
        """Inject text using ydotool"""
        try:
            subprocess.run(['ydotool', 'type', text], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"ydotool injection failed: {e}")
            return False
    
    def _inject_text_clipboard(self, text: str) -> bool:
        """Inject text using clipboard and paste simulation"""
        try:
            # Save current clipboard
            old_clip_result = subprocess.run(['wl-paste'], 
                                           capture_output=True, text=True)
            old_clipboard = old_clip_result.stdout if old_clip_result.returncode == 0 else ""
            
            # Copy new text
            subprocess.run(['wl-copy'], input=text, text=True, check=True)
            
            # Simulate Ctrl+V using available method
            if shutil.which('kdotool'):
                subprocess.run(['kdotool', 'key', 'ctrl+v'], check=True)
            elif shutil.which('ydotool'):
                # ydotool uses scan codes: 29=ctrl, 47=v
                subprocess.run(['ydotool', 'key', '29:1', '47:1', '47:0', '29:0'], 
                             check=True)
            else:
                logger.error("No method available to simulate Ctrl+V")
                return False
            
            # Restore old clipboard after a brief delay
            subprocess.run(['sh', '-c', f'sleep 0.1 && echo -n "{old_clipboard}" | wl-copy &'])
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Clipboard injection failed: {e}")
            return False
    
    # === Resource Management ===
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources"""
        if self.bus:
            self.bus.disconnect()
            self.bus = None
    
    def close(self):
        """Close resources for sync usage"""
        if self.loop:
            self.loop.close()
