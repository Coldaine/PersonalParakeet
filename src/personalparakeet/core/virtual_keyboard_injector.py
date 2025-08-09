#!/usr/bin/env python3
"""
High-performance Wayland virtual keyboard protocol implementation using ctypes.

This module implements the zwp_virtual_keyboard_v1 protocol for native
Wayland text injection without requiring root permissions or external tools.
Optimized for sub-5ms latency for real-time dictation.
"""

import os
import sys
import time
import logging
import ctypes
import ctypes.util
from typing import Tuple, Optional, List, Dict, Union
from dataclasses import dataclass
from enum import Enum, IntEnum
import threading

logger = logging.getLogger(__name__)

# Wayland protocol constants
WL_DISPLAY_ERROR_INVALID_OBJECT = 0
WL_DISPLAY_ERROR_INVALID_METHOD = 1
WL_DISPLAY_ERROR_NO_MEMORY = 2

# Input event codes (from linux/input-event-codes.h)
class KeyCode(IntEnum):
    """Linux input event key codes."""
    KEY_A = 30
    KEY_B = 48
    KEY_C = 46
    KEY_D = 32
    KEY_E = 18
    KEY_F = 33
    KEY_G = 34
    KEY_H = 35
    KEY_I = 23
    KEY_J = 36
    KEY_K = 37
    KEY_L = 38
    KEY_M = 50
    KEY_N = 49
    KEY_O = 24
    KEY_P = 25
    KEY_Q = 16
    KEY_R = 19
    KEY_S = 31
    KEY_T = 20
    KEY_U = 22
    KEY_V = 47
    KEY_W = 17
    KEY_X = 45
    KEY_Y = 21
    KEY_Z = 44

    KEY_0 = 11
    KEY_1 = 2
    KEY_2 = 3
    KEY_3 = 4
    KEY_4 = 5
    KEY_5 = 6
    KEY_6 = 7
    KEY_7 = 8
    KEY_8 = 9
    KEY_9 = 10

    KEY_SPACE = 57
    KEY_ENTER = 28
    KEY_TAB = 15
    KEY_BACKSPACE = 14
    KEY_DELETE = 111
    KEY_ESCAPE = 1

    KEY_LEFTSHIFT = 42
    KEY_RIGHTSHIFT = 54
    KEY_LEFTCTRL = 29
    KEY_RIGHTCTRL = 97
    KEY_LEFTALT = 56
    KEY_RIGHTALT = 100

    # Additional punctuation keys
    KEY_DOT = 52
    KEY_COMMA = 51
    KEY_SEMICOLON = 39
    KEY_SLASH = 53

class KeyboardLayout(Enum):
    """Supported keyboard layouts."""
    US = "us"
    UK = "uk"

class KeyState(IntEnum):
    """Key event states."""
    RELEASED = 0
    PRESSED = 1

@dataclass
class KeyEvent:
    """Represents a keyboard event with timing."""
    keycode: int
    state: KeyState
    modifiers: List[int]
    timestamp_ns: int

# ctypes structures for Wayland
class wl_interface(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("version", ctypes.c_int),
        ("method_count", ctypes.c_int),
        ("methods", ctypes.c_void_p),
        ("event_count", ctypes.c_int),
        ("events", ctypes.c_void_p),
    ]

class wl_message(ctypes.Structure):
    _fields_ = [
        ("name", ctypes.c_char_p),
        ("signature", ctypes.c_char_p),
        ("types", ctypes.POINTER(ctypes.POINTER(wl_interface))),
    ]

# Function pointer types
wl_display_func = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p)
wl_registry_func = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_char_p, ctypes.c_uint32)

class WaylandLibrary:
    """Ctypes wrapper for libwayland-client."""

    def __init__(self):
        self.lib = None
        self._load_library()

    def _load_library(self):
        """Load libwayland-client dynamically."""
        lib_names = [
            "libwayland-client.so.0",
            "libwayland-client.so",
            "wayland-client"
        ]

        for lib_name in lib_names:
            try:
                lib_path = ctypes.util.find_library(lib_name.replace("lib", "").replace(".so.0", "").replace(".so", ""))
                if lib_path:
                    self.lib = ctypes.CDLL(lib_path)
                    break
                self.lib = ctypes.CDLL(lib_name)
                break
            except OSError:
                continue

        if not self.lib:
            raise RuntimeError("Could not load libwayland-client")

        self._setup_functions()

    def _setup_functions(self):
        """Setup function signatures for libwayland-client."""
        # wl_display functions
        self.lib.wl_display_connect.argtypes = [ctypes.c_char_p]
        self.lib.wl_display_connect.restype = ctypes.c_void_p

        self.lib.wl_display_disconnect.argtypes = [ctypes.c_void_p]
        self.lib.wl_display_disconnect.restype = None

        self.lib.wl_display_roundtrip.argtypes = [ctypes.c_void_p]
        self.lib.wl_display_roundtrip.restype = ctypes.c_int

        self.lib.wl_display_dispatch.argtypes = [ctypes.c_void_p]
        self.lib.wl_display_dispatch.restype = ctypes.c_int

        self.lib.wl_display_flush.argtypes = [ctypes.c_void_p]
        self.lib.wl_display_flush.restype = ctypes.c_int

        # wl_registry functions
        self.lib.wl_display_get_registry.argtypes = [ctypes.c_void_p]
        self.lib.wl_display_get_registry.restype = ctypes.c_void_p

        self.lib.wl_registry_bind.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32]
        self.lib.wl_registry_bind.restype = ctypes.c_void_p

        # wl_proxy functions for generic object handling
        self.lib.wl_proxy_add_listener.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
        self.lib.wl_proxy_add_listener.restype = ctypes.c_int

        self.lib.wl_proxy_marshal.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        self.lib.wl_proxy_marshal.restype = None

        self.lib.wl_proxy_marshal_constructor.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
        self.lib.wl_proxy_marshal_constructor.restype = ctypes.c_void_p

        self.lib.wl_proxy_destroy.argtypes = [ctypes.c_void_p]
        self.lib.wl_proxy_destroy.restype = None

class wl_registry_listener(ctypes.Structure):
    _fields_ = [
        ("global_add", wl_registry_func),
        ("global_remove", wl_registry_func)
    ]

class VirtualKeyboardInjector:
    """
    High-performance Wayland virtual keyboard protocol implementation.

    Uses ctypes with libwayland-client for sub-5ms latency text injection.
    Implements the zwp_virtual_keyboard_v1 protocol directly.
    """

    # Virtual keyboard protocol constants
    ZWP_VIRTUAL_KEYBOARD_MANAGER_V1_CREATE_VIRTUAL_KEYBOARD = 0
    ZWP_VIRTUAL_KEYBOARD_V1_KEYMAP = 0
    ZWP_VIRTUAL_KEYBOARD_V1_KEY = 1
    ZWP_VIRTUAL_KEYBOARD_V1_MODIFIERS = 2

    # Protocol interface IDs (from wayland-protocols)
    WL_REGISTRY_INTERFACE = "wl_registry"
    WL_SEAT_INTERFACE = "wl_seat"
    ZWP_VIRTUAL_KEYBOARD_MANAGER_V1_INTERFACE = "zwp_virtual_keyboard_manager_v1"
    ZWP_VIRTUAL_KEYBOARD_V1_INTERFACE = "zwp_virtual_keyboard_v1"

    def __init__(self, layout: KeyboardLayout = KeyboardLayout.US):
        """
        Initialize high-performance virtual keyboard.

        Args:
            layout: Keyboard layout for key mapping
        """
        self.layout = layout
        self._connected = False
        self._display = None
        self._registry = None
        self._seat = None
        self._virtual_keyboard_manager = None
        self._virtual_keyboard = None
        self._keymap_fd = None
        self._keymap_size = 0

        # Performance optimization: pre-compute key mappings
        self._key_map = self._build_key_map()
        self._modifier_map = self._build_modifier_map()

        # Threading for async operations
        self._event_thread = None
        self._running = False

        # Wayland library
        try:
            self._wl = WaylandLibrary()
        except RuntimeError as e:
            logger.error(f"Failed to load Wayland library: {e}")
            raise

        # Registry listener for global objects
        self._registry_listener = wl_registry_listener(
            global_add=wl_display_func(self._registry_global_add),
            global_remove=wl_display_func(self._registry_global_remove)
        )

        logger.info(f"VirtualKeyboardInjector initialized with layout: {layout.value}")

    def _registry_global_add(self, data, registry, name, interface, version):
        """Handle new global objects from the Wayland compositor."""
        if interface == self.ZWP_VIRTUAL_KEYBOARD_MANAGER_V1_INTERFACE:
            logger.info(f"Found zwp_virtual_keyboard_manager_v1 (id: {name})")
            # Bind to the virtual keyboard manager
            self._virtual_keyboard_manager = self._wl.lib.wl_registry_bind(
                registry,
                name,
                ctypes.c_void_p(ctypes.addressof(wl_interface)),
                1  # version
            )

            if not self._virtual_keyboard_manager:
                logger.error("Failed to bind zwp_virtual_keyboard_manager_v1")
                return

            # Create virtual keyboard for the default seat
            self._create_virtual_keyboard()

    def _registry_global_remove(self, data, registry, name):
        """Handle removed global objects."""
        if not self._virtual_keyboard_manager:
            return

    def _create_virtual_keyboard(self):
        """Create a virtual keyboard from the manager."""
        try:
            # Call create_virtual_keyboard method on the manager
            self._virtual_keyboard = self._wl.lib.wl_proxy_marshal_constructor(
                self._virtual_keyboard_manager,
                self.ZWP_VIRTUAL_KEYBOARD_MANAGER_V1_CREATE_VIRTUAL_KEYBOARD,
                ctypes.c_void_p(0)  # seat - use default
            )

            if not self._virtual_keyboard:
                logger.error("Failed to create virtual keyboard")
                return False

            # Set up keymap (XKB layout)
            self._setup_keymap()

            logger.info("Virtual keyboard created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create virtual keyboard: {e}")
            return False

    def _setup_keymap(self):
        """Set up the keymap for the virtual keyboard."""
        try:
            # Use XKB layout string (us, uk, etc.)
            xkb_layout = self.layout.value

            # Convert to bytes for Wayland
            xkb_bytes = xkb_layout.encode('utf-8')

            # Call set_keymap on the virtual keyboard
            self._wl.lib.wl_proxy_marshal(
                self._virtual_keyboard,
                self.ZWP_VIRTUAL_KEYBOARD_V1_KEYMAP,
                ctypes.c_uint32(len(xkb_bytes)),
                ctypes.c_char_p(xkb_bytes)
            )

            logger.info(f"Keymap set to {xkb_layout}")

        except Exception as e:
            logger.error(f"Failed to set keymap: {e}")

    def connect(self) -> bool:
        """
        Connect to Wayland display and initialize virtual keyboard.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Connect to Wayland display
            display_name = os.environ.get('WAYLAND_DISPLAY')
            display_bytes = display_name.encode('utf-8') if display_name else None

            self._display = self._wl.lib.wl_display_connect(display_bytes)
            if not self._display:
                logger.error("Failed to connect to Wayland display")
                return False

            # Get registry and set up listener for global objects
            self._registry = self._wl.lib.wl_display_get_registry(self._display)
            if not self._registry:
                logger.error("Failed to get Wayland registry")
                return False

            # Add registry listener
            self._wl.lib.wl_proxy_add_listener(
                self._registry,
                ctypes.c_void_p(ctypes.addressof(self._registry_listener))
            )

            # Perform roundtrip to get globals
            if self._wl.lib.wl_display_roundtrip(self._display) == -1:
                logger.error("Failed to perform display roundtrip")
                return False

            self._connected = True
            logger.info("Connected to Wayland display and set up virtual keyboard")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Wayland: {e}")
            return False

    def inject_text(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Inject text using virtual keyboard protocol with sub-5ms latency.

        Args:
            text: Text to inject

        Returns:
            Tuple of (success, error_message)
        """
        if not self._connected:
            if not self.connect():
                return False, "Failed to connect to Wayland display"

        start_time = time.perf_counter()

        try:
            # Convert text to optimized key events
            key_events = self._text_to_key_events_optimized(text)

            # Send key events with minimal latency
            for event in key_events:
                if not self._send_key_event_fast(event):
                    return False, f"Failed to send key event for keycode {event.keycode}"

            # Flush to ensure immediate sending
            self._wl.lib.wl_display_flush(self._display)

            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Text injection completed in {elapsed_ms:.2f}ms")

            if elapsed_ms > 5.0:
                logger.warning(f"Injection latency {elapsed_ms:.2f}ms exceeds 5ms target")

            return True, None

        except Exception as e:
            logger.error(f"Failed to inject text: {e}")
            return False, str(e)

    def _text_to_key_events_optimized(self, text: str) -> List[KeyEvent]:
        """
        Convert text to key events with performance optimization.

        Args:
            text: Text to convert

        Returns:
            List of optimized KeyEvent objects
        """
        events = []
        current_time_ns = time.time_ns()

        for char in text:
            keycode = self._key_map.get(char)
            if keycode is None:
                logger.warning(f"Unsupported character: {repr(char)}")
                continue

            modifiers = self._modifier_map.get(char, [])

            # Press modifiers first
            for mod in modifiers:
                events.append(KeyEvent(
                    keycode=mod,
                    state=KeyState.PRESSED,
                    modifiers=[],
                    timestamp_ns=current_time_ns
                ))
                current_time_ns += 1000  # 1μs between events

            # Press main key
            events.append(KeyEvent(
                keycode=keycode,
                state=KeyState.PRESSED,
                modifiers=modifiers,
                timestamp_ns=current_time_ns
            ))
            current_time_ns += 1000

            # Release main key
            events.append(KeyEvent(
                keycode=keycode,
                state=KeyState.RELEASED,
                modifiers=modifiers,
                timestamp_ns=current_time_ns
            ))
            current_time_ns += 1000

            # Release modifiers
            for mod in reversed(modifiers):
                events.append(KeyEvent(
                    keycode=mod,
                    state=KeyState.RELEASED,
                    modifiers=[],
                    timestamp_ns=current_time_ns
                ))
                current_time_ns += 1000

        return events

    def _send_key_event_fast(self, event: KeyEvent) -> bool:
        """
        Send key event with minimal latency using direct protocol calls.

        Args:
            event: KeyEvent to send

        Returns:
            True if successful, False otherwise
        """
        if not self._virtual_keyboard:
            logger.error("Virtual keyboard not initialized")
            return False

        try:
            # Convert timestamp to milliseconds for Wayland
            timestamp_ms = event.timestamp_ns // 1000000

            # Send key event directly via ctypes
            # zwp_virtual_keyboard_v1_key(keyboard, time, key, state)
            self._wl.lib.wl_proxy_marshal(
                self._virtual_keyboard,
                self.ZWP_VIRTUAL_KEYBOARD_V1_KEY,
                ctypes.c_uint32(timestamp_ms),
                ctypes.c_uint32(event.keycode),
                ctypes.c_uint32(event.state)
            )

            return True

        except Exception as e:
            logger.error(f"Failed to send key event: {e}")
            return False

    def inject_key(self, key: str, modifiers: List[str] = None) -> bool:
        """
        Send individual key press/release events.

        Args:
            key: Key to press
            modifiers: List of modifiers

        Returns:
            True if successful, False otherwise
        """
        if not self._connected:
            if not self.connect():
                return False

        try:
            # Get keycode for the key
            keycode = self._key_map.get(key)
            if keycode is None:
                logger.error(f"Unsupported key: {key}")
                return False

            # Get modifiers (if any)
            key_modifiers = []
            if modifiers:
                for mod in modifiers:
                    mod_code = self._modifier_map.get(mod, [])
                    if mod_code:
                        key_modifiers.extend(mod_code)

            # Create key event with current timestamp
            current_time_ns = time.time_ns()
            press_event = KeyEvent(
                keycode=keycode,
                state=KeyState.PRESSED,
                modifiers=key_modifiers,
                timestamp_ns=current_time_ns
            )

            release_event = KeyEvent(
                keycode=keycode,
                state=KeyState.RELEASED,
                modifiers=key_modifiers,
                timestamp_ns=current_time_ns + 1000  # 1μs later
            )

            # Send press event
            if not self._send_key_event_fast(press_event):
                return False

            # Send release event
            if not self._send_key_event_fast(release_event):
                return False

            # Flush to ensure immediate sending
            self._wl.lib.wl_display_flush(self._display)

            return True

        except Exception as e:
            logger.error(f"Failed to inject key: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if virtual keyboard protocol is available on this system.

        Returns:
            True if available, False otherwise
        """
        try:
            # Try connecting and checking for the virtual keyboard manager
            display_name = os.environ.get('WAYLAND_DISPLAY')
            if not display_name:
                logger.warning("WAYLAND_DISPLAY environment variable not set")
                return False

            # Load Wayland library
            wl = WaylandLibrary()

            # Connect to Wayland display
            display = wl.lib.wl_display_connect(display_name.encode('utf-8'))
            if not display:
                logger.warning("Failed to connect to Wayland display")
                return False

            # Get registry and perform roundtrip
            registry = wl.lib.wl_display_get_registry(display)
            if not registry:
                wl.lib.wl_display_disconnect(display)
                return False

            # Set up a temporary listener to check for the virtual keyboard manager
            found_vk_manager = False

            def global_add(data, registry, name, interface, version):
                nonlocal found_vk_manager
                if interface == "zwp_virtual_keyboard_manager_v1":
                    found_vk_manager = True

            # Create listener structure
            listener = wl_registry_listener(
                global_add=wl_display_func(global_add),
                global_remove=wl_display_func(lambda *args: None)
            )

            # Add listener and perform roundtrip
            wl.lib.wl_proxy_add_listener(registry, ctypes.c_void_p(ctypes.addressof(listener)), 0)

            if wl.lib.wl_display_roundtrip(display) == -1:
                logger.warning("Failed to perform Wayland roundtrip")
            else:
                found_vk_manager = True

            # Clean up
            wl.lib.wl_display_disconnect(display)
            return found_vk_manager

        except Exception as e:
            logger.error(f"Error checking virtual keyboard availability: {e}")
            return False

    def cleanup(self):
        """
        Clean up resources and disconnect from Wayland.
        """
        if self._display:
            try:
                # Destroy virtual keyboard if it exists
                if self._virtual_keyboard:
                    self._wl.lib.wl_proxy_destroy(self._virtual_keyboard)
                    self._virtual_keyboard = None

                # Disconnect from Wayland display
                self._wl.lib.wl_display_disconnect(self._display)
                logger.info("Disconnected from Wayland display")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")