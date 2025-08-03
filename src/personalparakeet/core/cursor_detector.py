#!/usr/bin/env python3
"""
Cursor Detector - This module provides cursor position detection for thought linking.
To activate: Enable thought_linking in config

Detects significant cursor movements to help determine if user has
moved to a different input context.
"""

import logging
import platform
import math
import time
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class CursorPosition:
    """Cursor position information"""
    x: int
    y: int
    timestamp: float
    screen_id: Optional[int] = None


class CursorDetector:
    """
    Cross-platform cursor position detection.
    
    Detects cursor movements to inform thought linking decisions.
    """
    
    def __init__(self, enabled: bool = False, movement_threshold: int = 100):
        """
        Initialize cursor detector
        
        Args:
            enabled: Whether detection is active
            movement_threshold: Pixels of movement to consider significant
        """
        self.enabled = enabled
        self.movement_threshold = movement_threshold
        self.platform = platform.system().lower()
        
        self._last_position: Optional[CursorPosition] = None
        self._platform_initialized = False
        
        logger.info(f"CursorDetector initialized (enabled={enabled}, platform={self.platform})")
        if self.enabled:
            self._initialize_platform()

    def _initialize_platform(self):
        """Initialize platform-specific dependencies"""
        if self._platform_initialized or not self.enabled:
            return
            
        try:
            if self.platform == "windows":
                self._init_windows()
            elif self.platform == "linux":
                self._init_linux()
            elif self.platform == "darwin":
                self._init_macos()
            else:
                logger.warning(f"Unsupported platform for cursor detection: {self.platform}")
                self.enabled = False
                
            if self.enabled:
                self._platform_initialized = True
        except Exception as e:
            logger.error(f"Failed to initialize cursor detection: {e}")
            self.enabled = False

    def _init_windows(self):
        """Initialize Windows-specific dependencies"""
        try:
            import win32api
            self._win32api = win32api
            logger.debug("Windows cursor detection initialized")
        except ImportError:
            logger.warning("pywin32 not installed. Run 'pip install pywin32' for cursor detection on Windows.")
            self.enabled = False

    def _init_linux(self):
        """Initialize Linux-specific dependencies"""
        try:
            from Xlib import display
            self._display = display.Display()
            self._screen = self._display.screen()
            logger.debug("Linux cursor detection initialized")
        except ImportError:
            logger.warning("python-xlib not installed. Run 'pip install python-xlib' for cursor detection on Linux.")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Xlib for cursor detection: {e}")
            self.enabled = False

    def _init_macos(self):
        """Initialize macOS-specific dependencies"""
        try:
            import Quartz
            self._quartz = Quartz
            logger.debug("macOS cursor detection initialized")
        except ImportError:
            logger.warning("pyobjc-framework-Quartz not installed. Run 'pip install pyobjc-framework-Quartz' for cursor detection on macOS.")
            self.enabled = False

    def get_cursor_position(self) -> Optional[Tuple[int, int]]:
        """
        Get current cursor position
        
        Returns:
            Tuple of (x, y) coordinates if successful, None if disabled or error
        """
        if not self.enabled or not self._platform_initialized:
            return None

        try:
            if self.platform == "windows":
                return self._get_position_windows()
            elif self.platform == "linux":
                return self._get_position_linux()
            elif self.platform == "darwin":
                return self._get_position_macos()
        except Exception as e:
            logger.error(f"Error getting cursor position on {self.platform}: {e}")
            self.enabled = False # Disable on error to avoid repeated failures
        return None

    def _get_position_windows(self) -> Optional[Tuple[int, int]]:
        """Get cursor position on Windows"""
        if hasattr(self, '_win32api'):
            return self._win32api.GetCursorPos()
        return None

    def _get_position_linux(self) -> Optional[Tuple[int, int]]:
        """Get cursor position on Linux"""
        if hasattr(self, '_screen'):
            pointer = self._screen.root.query_pointer()
            return pointer.root_x, pointer.root_y
        return None

    def _get_position_macos(self) -> Optional[Tuple[int, int]]:
        """Get cursor position on macOS"""
        if hasattr(self, '_quartz'):
            event = self._quartz.CGEventCreate(None)
            location = self._quartz.CGEventGetLocation(event)
            return int(location.x), int(location.y)
        return None
    
    def calculate_movement_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """
        Calculate Euclidean distance between two positions
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            Distance in pixels
        """
        return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)
    
    def check_significant_movement(self) -> Tuple[bool, float]:
        """
        Check if cursor has moved significantly since last check
        
        Returns:
            Tuple of (has_moved_significantly, distance_moved)
        """
        if not self.enabled:
            return False, 0.0
            
        current_pos = self.get_cursor_position()
        if current_pos is None:
            return False, 0.0
            
        if self._last_position is None:
            self._last_position = CursorPosition(
                x=current_pos[0],
                y=current_pos[1],
                timestamp=time.time()
            )
            return False, 0.0
            
        # Calculate distance
        last_pos = (self._last_position.x, self._last_position.y)
        distance = self.calculate_movement_distance(last_pos, current_pos)
        
        # Check if significant
        is_significant = distance >= self.movement_threshold
        
        if is_significant:
            logger.debug(f"Significant cursor movement: {distance:.0f} pixels")
            self._last_position = CursorPosition(
                x=current_pos[0],
                y=current_pos[1],
                timestamp=time.time()
            )
            
        return is_significant, distance
    
    def get_movement_signal_strength(self, distance: float) -> float:
        """
        Calculate signal strength based on movement distance
        
        Args:
            distance: Distance moved in pixels
            
        Returns:
            Signal strength from 0.0 to 1.0
        """
        if distance < self.movement_threshold:
            return 0.0
            
        # Linear scaling up to 2x threshold
        strength = min(1.0, distance / (self.movement_threshold * 2))
        
        # Apply curve for more natural response
        return min(0.8, strength * 0.9)
    
    def get_cursor_context(self) -> Dict[str, Any]:
        """
        Get cursor context information for thought linking
        
        Returns:
            Dictionary with cursor context data
        """
        if not self.enabled:
            return {"enabled": False}
            
        current_pos = self.get_cursor_position()
        if current_pos is None:
            return {"enabled": True, "detected": False}
            
        context = {
            "enabled": True,
            "detected": True,
            "position": {"x": current_pos[0], "y": current_pos[1]},
            "threshold": self.movement_threshold
        }
        
        if self._last_position:
            last_pos = (self._last_position.x, self._last_position.y)
            distance = self.calculate_movement_distance(last_pos, current_pos)
            context["distance_from_last"] = distance
            context["is_significant"] = distance >= self.movement_threshold
            
        return context
    
    def reset(self):
        """Reset cursor tracking state"""
        self._last_position = None
        logger.debug("Cursor detector state reset")


def create_cursor_detector(enabled: bool = False, movement_threshold: int = 100) -> CursorDetector:
    """Factory function to create a cursor detector"""
    return CursorDetector(enabled=enabled, movement_threshold=movement_threshold)