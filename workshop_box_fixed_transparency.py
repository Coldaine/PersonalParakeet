#!/usr/bin/env python3
"""
Workshop Box with Fixed Transparency for Windows
Using Windows-specific APIs for true blur/acrylic effects
"""

import sys
import ctypes
from ctypes import wintypes
from typing import Optional

from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    QRect, QPoint, pyqtSignal, QRectF
)
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QFontMetrics, 
    QPainterPath, QLinearGradient, QBrush, QPen
)
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout


# Windows-specific constants for DWM
class ACCENT_STATE:
    DISABLED = 0
    ENABLE_GRADIENT = 1
    ENABLE_TRANSPARENTGRADIENT = 2
    ENABLE_BLURBEHIND = 3
    ENABLE_ACRYLICBLURBEHIND = 4
    INVALID_STATE = 5


class ACCENT_POLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_uint),
        ("AccentFlags", ctypes.c_uint),
        ("GradientColor", ctypes.c_uint),
        ("AnimationId", ctypes.c_uint),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("Data", ctypes.POINTER(ctypes.c_int)),
        ("SizeOfData", ctypes.c_ulong),
    ]


def enable_acrylic_blur(hwnd: int, accent_state: int = ACCENT_STATE.ENABLE_ACRYLICBLURBEHIND):
    """Enable Windows 10/11 acrylic blur effect"""
    
    # Load Windows DLLs
    user32 = ctypes.windll.user32
    set_window_composition_attribute = user32.SetWindowCompositionAttribute
    
    # Create accent policy
    accent = ACCENT_POLICY()
    accent.AccentState = accent_state
    accent.AccentFlags = 2  # ACCENT_ENABLE_BLURBEHIND
    accent.GradientColor = 0x01000000  # Transparent background
    accent.AnimationId = 0
    
    # Create data structure
    data = WINDOWCOMPOSITIONATTRIBDATA()
    data.Attribute = 19  # WCA_ACCENT_POLICY
    data.SizeOfData = ctypes.sizeof(accent)
    data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.POINTER(ctypes.c_int))
    
    # Apply the composition
    set_window_composition_attribute(hwnd, ctypes.pointer(data))


class ModernWorkshopBox(QWidget):
    """Modern Workshop Box with proper Windows transparency"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.current_text = ""
        
        # Apply Windows blur after window is shown
        QTimer.singleShot(100, self.apply_windows_effects)
        
    def init_ui(self):
        # Window flags for borderless, always-on-top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # Enable transparency
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        
        # Layout with no margins for full control
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        # Initial size
        self.resize(500, 100)
        
        # Center on screen
        screen = QApplication.primaryScreen()
        if screen:
            screen_rect = screen.geometry()
            self.move(
                screen_rect.center().x() - self.width() // 2,
                screen_rect.center().y() - self.height() // 2
            )
    
    def apply_windows_effects(self):
        """Apply Windows-specific blur effects"""
        # Get window handle
        hwnd = int(self.winId())
        
        # Try acrylic blur first (Windows 10 1803+)
        try:
            enable_acrylic_blur(hwnd, ACCENT_STATE.ENABLE_ACRYLICBLURBEHIND)
        except:
            # Fallback to regular blur
            try:
                enable_acrylic_blur(hwnd, ACCENT_STATE.ENABLE_BLURBEHIND)
            except:
                print("Warning: Could not enable Windows blur effects")
    
    def paintEvent(self, event):
        """Custom painting with modern design"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        # Create rounded rectangle path
        path = QPainterPath()
        rect = QRectF(self.rect()).adjusted(2, 2, -2, -2)
        path.addRoundedRect(rect, 20, 20)
        
        # Semi-transparent background
        bg_color = QColor(30, 30, 30, 180)  # Dark with transparency
        painter.fillPath(path, bg_color)
        
        # Subtle gradient overlay
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 20))
        gradient.setColorAt(1, QColor(255, 255, 255, 5))
        painter.fillPath(path, QBrush(gradient))
        
        # Border
        border_color = QColor(255, 255, 255, 40)
        painter.setPen(QPen(border_color, 1))
        painter.drawPath(path)
        
        # Draw text
        if self.current_text:
            painter.setPen(QColor(255, 255, 255, 230))
            font = QFont("Segoe UI", 12)
            painter.setFont(font)
            
            text_rect = rect.adjusted(20, 20, -20, -20)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.current_text)
        
        # Status indicator
        painter.setBrush(QColor(16, 185, 129, 200))  # Green
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(self.width() - 25, 15, 8, 8)
        
    def update_text(self, text: str):
        """Update the displayed text"""
        self.current_text = text
        self.update()  # Trigger repaint
        
        # Adjust size based on text
        font = QFont("Segoe UI", 12)
        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text) + 60  # Add padding
        text_height = fm.height() + 60
        
        # Smooth resize
        new_width = min(max(300, text_width), 800)
        new_height = min(max(80, text_height), 200)
        
        if (new_width, new_height) != (self.width(), self.height()):
            self.animate_resize(new_width, new_height)
    
    def animate_resize(self, target_width: int, target_height: int):
        """Smoothly animate to new size"""
        # Create geometry animation
        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(200)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        current_geo = self.geometry()
        # Keep centered while resizing
        new_x = current_geo.x() - (target_width - current_geo.width()) // 2
        new_y = current_geo.y() - (target_height - current_geo.height()) // 2
        target_geo = QRect(new_x, new_y, target_width, target_height)
        
        self.anim.setStartValue(current_geo)
        self.anim.setEndValue(target_geo)
        self.anim.start()
    
    def mousePressEvent(self, event):
        """Enable window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle window dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class SimpleDemo(QWidget):
    """Simple demo to test the Workshop Box"""
    
    def __init__(self, workshop_box):
        super().__init__()
        self.workshop_box = workshop_box
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Workshop Box Demo - Click to cycle text")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # Info label
        self.info_label = QLabel("Click this window to cycle through text examples")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        # Add instruction
        instruction = QLabel("The Workshop Box has proper transparency and blur!")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(instruction)
        
        self.setLayout(layout)
        
        # Text examples
        self.texts = [
            "Hello world",
            "PersonalParakeet with real-time transcription",
            "The Workshop Box adapts its size dynamically based on content",
            "Voice commands activated",
            ""
        ]
        self.current_index = 0
        
    def mousePressEvent(self, event):
        """Cycle through texts on click"""
        text = self.texts[self.current_index]
        self.workshop_box.update_text(text)
        self.current_index = (self.current_index + 1) % len(self.texts)
        
        if text:
            self.info_label.setText(f"Showing: {text[:30]}...")
        else:
            self.info_label.setText("Empty text")


def main():
    app = QApplication(sys.argv)
    
    # Create and show workshop box
    workshop = ModernWorkshopBox()
    workshop.show()
    
    # Create demo controller
    demo = SimpleDemo(workshop)
    demo.show()
    demo.move(50, 50)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()