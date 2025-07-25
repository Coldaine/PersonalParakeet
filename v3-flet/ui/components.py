#!/usr/bin/env python3
"""
Reusable Flet UI components for PersonalParakeet v3
Replaces React components with Flet equivalents
"""

import flet as ft
from typing import Callable, Optional


class StatusIndicator:
    """Status indicator showing connection and listening state"""
    
    def __init__(self, is_connected: bool, is_listening: bool):
        self.is_connected = is_connected
        self.is_listening = is_listening
        self.container = None
    
    def build(self) -> ft.Container:
        """Build the status indicator UI"""
        # Determine status color and tooltip
        if not self.is_connected:
            color = ft.Colors.RED_500
            tooltip = "Disconnected from backend"
        elif self.is_listening:
            color = ft.Colors.GREEN_500
            tooltip = "Listening..."
        else:
            color = ft.Colors.GREY_500
            tooltip = "Connected but not listening"
        
        self.container = ft.Container(
            content=ft.Icon(
                ft.Icons.MIC if self.is_listening else ft.Icons.MIC_OFF,
                color=color,
                size=20
            ),
            tooltip=tooltip,
            animate=ft.animation.Animation(1000) if self.is_listening else None,
        )
        
        return self.container
    
    def update_state(self, is_connected: bool, is_listening: bool):
        """Update the indicator state"""
        self.is_connected = is_connected
        self.is_listening = is_listening
        
        if self.container:
            # Update icon and color
            if not is_connected:
                self.container.content.name = ft.Icons.MIC_OFF
                self.container.content.color = ft.Colors.RED_500
                self.container.tooltip = "Disconnected from backend"
            elif is_listening:
                self.container.content.name = ft.Icons.MIC
                self.container.content.color = ft.Colors.GREEN_500
                self.container.tooltip = "Listening..."
            else:
                self.container.content.name = ft.Icons.MIC_OFF
                self.container.content.color = ft.Colors.GREY_500
                self.container.tooltip = "Connected but not listening"


class VADIndicator:
    """Voice Activity Detection indicator with audio level"""
    
    def __init__(self, vad_status: dict):
        self.vad_status = vad_status
        self.container = None
        self.level_bar = None
    
    def build(self) -> ft.Container:
        """Build the VAD indicator UI"""
        # Audio level progress bar
        self.level_bar = ft.ProgressBar(
            value=self.vad_status.get('rms_energy', 0.0),
            width=80,
            height=4,
            color=ft.Colors.BLUE_500 if self.vad_status.get('is_speaking', False) else ft.Colors.GREY_500,
            bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.GREY),
        )
        
        self.container = ft.Container(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.GRAPHIC_EQ,
                    color=ft.Colors.BLUE_500 if self.vad_status.get('is_speaking', False) else ft.Colors.GREY_500,
                    size=16
                ),
                self.level_bar,
            ], spacing=5, tight=True),
            tooltip="Voice activity level"
        )
        
        return self.container
    
    def update_status(self, vad_status: dict):
        """Update VAD status display"""
        self.vad_status = vad_status
        
        if self.level_bar:
            self.level_bar.value = min(1.0, vad_status.get('rms_energy', 0.0) * 10)  # Scale for visibility
            is_speaking = vad_status.get('is_speaking', False)
            self.level_bar.color = ft.Colors.BLUE_500 if is_speaking else ft.Colors.GREY_500
        
        if self.container and hasattr(self.container.content, 'controls'):
            icon = self.container.content.controls[0]
            icon.color = ft.Colors.BLUE_500 if vad_status.get('is_speaking', False) else ft.Colors.GREY_500


class ControlPanel:
    """Control panel with action buttons"""
    
    def __init__(self, clarity_enabled: bool, command_mode_enabled: bool,
                 on_toggle_clarity: Callable, on_commit_text: Callable, on_clear_text: Callable):
        self.clarity_enabled = clarity_enabled
        self.command_mode_enabled = command_mode_enabled
        self.on_toggle_clarity = on_toggle_clarity
        self.on_commit_text = on_commit_text
        self.on_clear_text = on_clear_text
        
        self.clarity_btn = None
        self.command_btn = None
        self.commit_btn = None
        self.clear_btn = None
        self.container = None
    
    def build(self) -> ft.Container:
        """Build the control panel UI"""
        # Clarity toggle button
        self.clarity_btn = ft.IconButton(
            icon=ft.Icons.AUTO_FIX_HIGH,
            icon_color=ft.Colors.AMBER_500 if self.clarity_enabled else ft.Colors.GREY_500,
            tooltip=f"Clarity Engine: {'ON' if self.clarity_enabled else 'OFF'}",
            on_click=lambda _: self.on_toggle_clarity()
        )
        
        # Command mode button (placeholder)
        self.command_btn = ft.IconButton(
            icon=ft.Icons.RECORD_VOICE_OVER,
            icon_color=ft.Colors.PURPLE_500 if self.command_mode_enabled else ft.Colors.GREY_500,
            tooltip=f"Command Mode: {'ON' if self.command_mode_enabled else 'OFF'}",
            disabled=True,  # Not implemented yet
        )
        
        # Commit button
        self.commit_btn = ft.IconButton(
            icon=ft.Icons.CHECK,
            icon_color=ft.Colors.GREEN_500,
            tooltip="Commit text (Ctrl+Enter)",
            on_click=lambda _: self.on_commit_text()
        )
        
        # Clear button
        self.clear_btn = ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_color=ft.Colors.RED_500,
            tooltip="Clear text (Escape)",
            on_click=lambda _: self.on_clear_text()
        )
        
        self.container = ft.Container(
            content=ft.Row([
                self.clarity_btn,
                self.command_btn,
                ft.VerticalDivider(width=1),
                self.commit_btn,
                self.clear_btn,
            ], tight=True, spacing=5)
        )
        
        return self.container
    
    def update_state(self, clarity_enabled: bool, command_mode_enabled: bool):
        """Update control panel state"""
        self.clarity_enabled = clarity_enabled
        self.command_mode_enabled = command_mode_enabled
        
        if self.clarity_btn:
            self.clarity_btn.icon_color = ft.Colors.AMBER_500 if clarity_enabled else ft.Colors.GREY_500
            self.clarity_btn.tooltip = f"Clarity Engine: {'ON' if clarity_enabled else 'OFF'}"
        
        if self.command_btn:
            self.command_btn.icon_color = ft.Colors.PURPLE_500 if command_mode_enabled else ft.Colors.GREY_500
            self.command_btn.tooltip = f"Command Mode: {'ON' if command_mode_enabled else 'OFF'}"


class ConfidenceBar:
    """Confidence indicator bar"""
    
    def __init__(self, confidence: float):
        self.confidence = confidence
        self.progress_bar = None
        self.container = None
    
    def build(self) -> ft.Container:
        """Build the confidence bar UI"""
        if self.confidence <= 0:
            self.container = ft.Container()  # Empty container if no confidence
            return self.container
        
        # Color based on confidence level
        if self.confidence > 0.9:
            color = ft.Colors.GREEN_500
        elif self.confidence > 0.7:
            color = ft.Colors.ORANGE_500
        else:
            color = ft.Colors.RED_500
        
        self.progress_bar = ft.ProgressBar(
            value=self.confidence,
            width=None,  # Full width
            height=3,
            color=color,
            bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.GREY),
        )
        
        self.container = ft.Container(
            content=ft.Column([
                ft.Text(
                    f"Confidence: {self.confidence:.0%}",
                    size=10,
                    color=ft.Colors.GREY_400,
                    text_align=ft.TextAlign.CENTER
                ),
                self.progress_bar,
            ], spacing=2),
            visible=self.confidence > 0
        )
        
        return self.container
    
    def update_confidence(self, confidence: float):
        """Update confidence display"""
        self.confidence = confidence
        
        if self.container:
            self.container.visible = confidence > 0
        
        if confidence > 0 and self.progress_bar:
            self.progress_bar.value = confidence
            
            # Update color
            if confidence > 0.9:
                self.progress_bar.color = ft.Colors.GREEN_500
            elif confidence > 0.7:
                self.progress_bar.color = ft.Colors.ORANGE_500
            else:
                self.progress_bar.color = ft.Colors.RED_500
            
            # Update text
            if self.container and self.container.content and hasattr(self.container.content, 'controls'):
                text_widget = self.container.content.controls[0]
                text_widget.value = f"Confidence: {confidence:.0%}"


class ThinkingIndicator:
    """Animated thinking indicator (particle effect simulation)"""
    
    def __init__(self):
        self.container = None
        self.is_thinking = False
    
    def build(self) -> ft.Container:
        """Build thinking indicator with animated dots"""
        dots = []
        for i in range(3):
            dots.append(
                ft.Container(
                    width=6,
                    height=6,
                    bgcolor=ft.Colors.BLUE_300,
                    border_radius=3,
                    animate=ft.animation.Animation(
                        duration=800,
                        curve=ft.AnimationCurve.EASE_IN_OUT
                    )
                )
            )
        
        self.container = ft.Container(
            content=ft.Row(dots, spacing=4, tight=True),
            visible=False  # Hidden by default
        )
        
        return self.container
    
    def start_thinking(self):
        """Start thinking animation"""
        self.is_thinking = True
        if self.container:
            self.container.visible = True
    
    def stop_thinking(self):
        """Stop thinking animation"""
        self.is_thinking = False
        if self.container:
            self.container.visible = False
