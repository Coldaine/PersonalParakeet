#!/usr/bin/env python3
"""
Workshop Box Prototype - Adaptive Sizing Demonstration
PersonalParakeet v2.0 UI Concept
"""

import sys
import math
from typing import Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    QRect, QPoint, pyqtSignal, QObject, pyqtProperty
)
from PyQt6.QtGui import QPainter, QColor, QFont, QFontMetrics, QScreen
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout


class BoxMode(Enum):
    COMPACT = "compact"
    STANDARD = "standard"
    EXTENDED = "extended"


@dataclass
class BoxStyle:
    bg_opacity: float
    border_opacity: float
    shadow_blur: int
    shadow_offset: int
    min_width: int
    max_width: int
    min_height: int
    max_height: int


# Style definitions for each mode
STYLES = {
    BoxMode.COMPACT: BoxStyle(
        bg_opacity=0.85, border_opacity=0.3, shadow_blur=10, shadow_offset=2,
        min_width=400, max_width=600, min_height=60, max_height=80
    ),
    BoxMode.STANDARD: BoxStyle(
        bg_opacity=0.88, border_opacity=0.4, shadow_blur=15, shadow_offset=3,
        min_width=600, max_width=900, min_height=80, max_height=200
    ),
    BoxMode.EXTENDED: BoxStyle(
        bg_opacity=0.92, border_opacity=0.5, shadow_blur=20, shadow_offset=5,
        min_width=900, max_width=1200, min_height=200, max_height=400
    ),
}


class AnimatedWidget(QObject):
    """Helper class for smooth property animations"""
    
    def __init__(self, widget: QWidget):
        super().__init__()
        self._widget = widget
        self._opacity = 1.0
        
    def _get_opacity(self) -> float:
        return self._opacity
        
    def _set_opacity(self, value: float):
        self._opacity = value
        self._widget.setWindowOpacity(value)
        
    opacity = pyqtProperty(float, _get_opacity, _set_opacity)


class WorkshopBox(QWidget):
    """Adaptive Workshop Box UI Component"""
    
    def __init__(self):
        super().__init__()
        self.current_mode = BoxMode.COMPACT
        self.current_text = ""
        self.scale_factor = 1.0
        self.init_ui()
        self.calculate_dpi_scale()
        
    def init_ui(self):
        # Window flags for transparent, always-on-top, borderless window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Enable transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Text display
        self.text_label = QLabel("PersonalParakeet Workshop Box")
        self.text_label.setWordWrap(True)
        self.text_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-family: 'Consolas', 'SF Mono', 'Ubuntu Mono', monospace;
                font-size: 14px;
                background-color: rgba(0, 0, 0, 0);
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.text_label)
        self.setLayout(layout)
        
        # Animation helper
        self.animator = AnimatedWidget(self)
        
        # Initial size
        self.resize(400, 80)
        
    def calculate_dpi_scale(self):
        """Calculate scaling factor based on screen DPI"""
        screen = QApplication.primaryScreen()
        if screen:
            dpi = screen.logicalDotsPerInch()
            width = screen.size().width()
            
            # DPI scaling
            dpi_scale = dpi / 96.0
            
            # Resolution scaling  
            resolution_scale = min(width / 1920.0, 2.0)
            
            # Use the larger scale
            self.scale_factor = max(dpi_scale, resolution_scale)
            
            # Update font size
            font = self.text_label.font()
            font.setPointSize(int(14 * self.scale_factor))
            self.text_label.setFont(font)
    
    def update_text(self, text: str):
        """Update displayed text and adapt size accordingly"""
        self.current_text = text
        self.text_label.setText(text)
        
        # Determine new mode based on word count
        word_count = len(text.split())
        new_mode = self.determine_mode(word_count)
        
        if new_mode != self.current_mode:
            self.transition_to_mode(new_mode)
        else:
            self.adapt_size_to_content()
    
    def determine_mode(self, word_count: int) -> BoxMode:
        """Determine appropriate mode based on word count"""
        if word_count <= 10:
            return BoxMode.COMPACT
        elif word_count <= 50:
            return BoxMode.STANDARD
        else:
            return BoxMode.EXTENDED
    
    def adapt_size_to_content(self):
        """Smoothly adapt size to fit current content"""
        style = STYLES[self.current_mode]
        
        # Calculate required size
        fm = QFontMetrics(self.text_label.font())
        text_rect = fm.boundingRect(
            QRect(0, 0, int(style.max_width * self.scale_factor), 10000),
            Qt.TextFlag.TextWordWrap,
            self.current_text
        )
        
        # Add padding
        padding = int(40 * self.scale_factor)
        target_width = min(
            text_rect.width() + padding,
            int(style.max_width * self.scale_factor)
        )
        target_height = min(
            text_rect.height() + padding,
            int(style.max_height * self.scale_factor)
        )
        
        # Ensure minimum size
        target_width = max(target_width, int(style.min_width * self.scale_factor))
        target_height = max(target_height, int(style.min_height * self.scale_factor))
        
        # Animate to new size
        self.animate_resize(target_width, target_height)
    
    def transition_to_mode(self, new_mode: BoxMode):
        """Transition to a new display mode"""
        self.current_mode = new_mode
        
        # Update window opacity
        style = STYLES[new_mode]
        self.animate_opacity(style.bg_opacity)
        
        # Update size
        self.adapt_size_to_content()
        
        # Update position based on mode
        self.update_position_for_mode()
    
    def animate_resize(self, target_width: int, target_height: int):
        """Smoothly animate resize"""
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(150)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        current_geo = self.geometry()
        target_geo = QRect(
            current_geo.x(),
            current_geo.y(),
            target_width,
            target_height
        )
        
        animation.setStartValue(current_geo)
        animation.setEndValue(target_geo)
        animation.start()
    
    def animate_opacity(self, target_opacity: float):
        """Smoothly animate window opacity"""
        animation = QPropertyAnimation(self.animator, b"opacity")
        animation.setDuration(200)
        animation.setStartValue(self.windowOpacity())
        animation.setEndValue(target_opacity)
        animation.start()
    
    def update_position_for_mode(self):
        """Update position based on current mode"""
        screen = QApplication.primaryScreen()
        if not screen:
            return
            
        screen_rect = screen.availableGeometry()
        cursor_pos = QApplication.instance().screens()[0].cursor().pos()
        
        if self.current_mode == BoxMode.COMPACT:
            # Position near cursor
            x = cursor_pos.x() + int(30 * self.scale_factor)
            y = cursor_pos.y() + int(30 * self.scale_factor)
        
        elif self.current_mode == BoxMode.STANDARD:
            # Smart offset from cursor
            x = cursor_pos.x() + int(50 * self.scale_factor)
            y = cursor_pos.y() + int(50 * self.scale_factor)
            
        else:  # EXTENDED
            # Dock to right edge
            margin = int(50 * self.scale_factor)
            x = screen_rect.width() - self.width() - margin
            y = screen_rect.height() // 2 - self.height() // 2
        
        # Ensure on screen
        x = max(0, min(x, screen_rect.width() - self.width()))
        y = max(0, min(y, screen_rect.height() - self.height()))
        
        # Animate position change
        self.animate_move(x, y)
    
    def animate_move(self, target_x: int, target_y: int):
        """Smoothly animate position"""
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(250 if self.current_mode == BoxMode.EXTENDED else 150)
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        animation.setStartValue(self.pos())
        animation.setEndValue(QPoint(target_x, target_y))
        animation.start()
    
    def paintEvent(self, event):
        """Custom paint for the workshop box"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        style = STYLES[self.current_mode]
        
        # Background with rounded corners
        bg_color = QColor(30, 30, 30, int(255 * style.bg_opacity))
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        radius = int(12 * self.scale_factor)
        painter.drawRoundedRect(self.rect(), radius, radius)
        
        # Border
        border_color = QColor(100, 100, 100, int(255 * style.border_opacity))
        painter.setPen(border_color)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(self.rect(), radius, radius)


class DemoController(QWidget):
    """Demo control panel for testing the Workshop Box"""
    
    def __init__(self, workshop_box: WorkshopBox):
        super().__init__()
        self.workshop_box = workshop_box
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Workshop Box Demo Controller")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # Demo text samples
        self.texts = [
            "Hello world",  # Compact
            "PersonalParakeet dictation system with real-time transcription",  # Standard  
            "The Workshop Box adapts its size based on content length. It provides three distinct modes: compact for short phrases, standard for normal sentences, and extended for longer paragraphs. Each mode has unique visual characteristics and positioning behavior designed to enhance the user experience while maintaining clarity and reducing distraction during dictation sessions.",  # Extended
        ]
        self.current_text_index = 0
        
        # Timer for cycling through texts
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_text)
        self.timer.start(3000)  # Change every 3 seconds
        
        # Label
        self.info_label = QLabel("Workshop Box will cycle through different sizes...")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
        
        # Show first text
        self.next_text()
        
    def next_text(self):
        """Cycle to next demo text"""
        text = self.texts[self.current_text_index]
        self.workshop_box.update_text(text)
        self.current_text_index = (self.current_text_index + 1) % len(self.texts)
        
        mode_name = self.workshop_box.current_mode.value.capitalize()
        word_count = len(text.split())
        self.info_label.setText(f"Mode: {mode_name} ({word_count} words)")


def main():
    app = QApplication(sys.argv)
    
    # Create workshop box
    workshop_box = WorkshopBox()
    workshop_box.show()
    
    # Create demo controller
    controller = DemoController(workshop_box)
    controller.show()
    
    # Position controller window
    screen = app.primaryScreen()
    if screen:
        controller.move(50, 50)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()