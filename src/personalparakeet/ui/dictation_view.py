#!/usr/bin/env python3
"""
DictationView - Floating UI for PersonalParakeet v3
Provides transparent, always-on-top dictation interface with Flet
"""

import asyncio
import logging
from typing import Optional, Callable
import flet as ft

from personalparakeet.core.thought_linker import LinkingDecision

logger = logging.getLogger(__name__)


class DictationView:
    """
    Floating dictation UI with transparent background
    Manages visual feedback for dictation state and displays recognized text
    """
    
    def __init__(self, config, profile_manager):
        self.config = config
        self.profile_manager = profile_manager
        self.page: Optional[ft.Page] = None
        self.main_container: Optional[ft.Container] = None
        self.status_text: Optional[ft.Text] = None
        self.recognized_text: Optional[ft.Text] = None
        self.is_recording = False
        self.settings_dialog: Optional[ft.AlertDialog] = None

    async def initialize(self, page: ft.Page):
        """Initialize the Flet UI components"""
        self.page = page
        
        # Configure window
        self.page.title = "PersonalParakeet v3"
        self.page.window_always_on_top = True
        self.page.window_frameless = True
        self.page.window_bgcolor = ft.colors.TRANSPARENT
        self.page.bgcolor = ft.colors.TRANSPARENT
        
        # Set window size and position
        self.page.window_width = 400
        self.page.window_height = 150
        self.page.window_top = 50
        self.page.window_right = 50
        
        # Create UI components
        self.status_text = ft.Text(
            "Ready",
            size=14,
            color=ft.colors.WHITE,
            weight=ft.FontWeight.BOLD
        )
        
        self.recognized_text = ft.Text(
            "",
            size=16,
            color=ft.colors.WHITE,
            max_lines=3
        )
        
        settings_button = ft.IconButton(
            icon=ft.icons.SETTINGS,
            icon_color=ft.colors.WHITE,
            on_click=self.open_settings_dialog,
        )

        # Main container with semi-transparent background
        self.main_container = ft.Container(
            content=ft.Column([
                ft.Row([self.status_text, settings_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=1, color=ft.colors.WHITE30),
                self.recognized_text
            ]),
            bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLACK),
            border_radius=10,
            padding=15,
            expand=True
        )
        
        # Add to page
        await self.page.add_async(self.main_container)

    async def open_settings_dialog(self, e):
        """Open the settings dialog."""
        self.settings_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Settings"),
            content=self.build_settings_content(),
            actions=[
                ft.TextButton("Close", on_click=self.close_settings_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = self.settings_dialog
        self.settings_dialog.open = True
        await self.page.update_async()

    def build_settings_content(self) -> ft.Column:
        """Build the content for the settings dialog."""
        thought_linking_switch = ft.Switch(
            label="Enable Thought Linking",
            value=self.config.thought_linking.enabled,
            on_change=self.toggle_thought_linking,
        )

        vad_threshold_slider = ft.Slider(
            min=0.5,
            max=5.0,
            divisions=9,
            value=self.config.vad.pause_threshold,
            label="VAD Pause Threshold: {value}s",
            on_change=self.update_vad_threshold,
        )

        return ft.Column(
            [
                thought_linking_switch,
                vad_threshold_slider,
            ]
        )

    async def toggle_thought_linking(self, e):
        """Toggle the thought linking feature."""
        self.config.thought_linking.enabled = e.data == "true"
        self.config.save_to_file()

    async def update_vad_threshold(self, e):
        """Update the VAD pause threshold."""
        self.config.vad.pause_threshold = float(e.data)
        self.config.save_to_file()

    async def close_settings_dialog(self, e):
        """Close the settings dialog."""
        self.settings_dialog.open = False
        await self.page.update_async()

    async def update_status(self, status: str, color: str = ft.colors.WHITE):
        """Update the status text"""
        if self.status_text:
            self.status_text.value = status
            self.status_text.color = color
            await self.page.update_async()
            
    async def update_text(self, text: str, decision: LinkingDecision = LinkingDecision.APPEND_WITH_SPACE):
        """Update the recognized text display"""
        if self.recognized_text:
            self.recognized_text.value = text
            if decision == LinkingDecision.START_NEW_THOUGHT:
                self.recognized_text.color = ft.colors.CYAN
            elif decision == LinkingDecision.START_NEW_PARAGRAPH:
                self.recognized_text.color = ft.colors.YELLOW
            else:
                self.recognized_text.color = ft.colors.WHITE
            await self.page.update_async()
            
    async def set_recording(self, is_recording: bool):
        """Update recording state visual feedback"""
        self.is_recording = is_recording
        if is_recording:
            await self.update_status("Recording...", ft.colors.RED)
            if self.main_container:
                self.main_container.border = ft.border.all(2, ft.colors.RED)
        else:
            await self.update_status("Ready", ft.colors.GREEN)
            if self.main_container:
                self.main_container.border = None
        await self.page.update_async()
        
    async def show_error(self, error: str):
        """Display error message"""
        await self.update_status(f"Error: {error}", ft.colors.ORANGE)
        
    def cleanup(self):
        """Cleanup UI resources"""
        logger.info("DictationView cleanup completed")