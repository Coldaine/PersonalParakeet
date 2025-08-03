#!/usr/bin/env python3
"""
DictationView - Floating UI for PersonalParakeet v3
Provides transparent, always-on-top dictation interface with Flet
"""

import asyncio
import logging
from typing import Optional, Callable
import flet as ft

logger = logging.getLogger(__name__)


class DictationView:
    """
    Floating dictation UI with transparent background
    Manages visual feedback for dictation state and displays recognized text
    """
    
    def __init__(self, config):
        self.config = config
        self.page: Optional[ft.Page] = None
        self.main_container: Optional[ft.Container] = None
        self.status_text: Optional[ft.Text] = None
        self.recognized_text: Optional[ft.Text] = None
        self.is_recording = False
        
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
        
        # Main container with semi-transparent background
        self.main_container = ft.Container(
            content=ft.Column([
                self.status_text,
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
        
    async def update_status(self, status: str, color: str = ft.colors.WHITE):
        """Update the status text"""
        if self.status_text:
            self.status_text.value = status
            self.status_text.color = color
            await self.page.update_async()
            
    async def update_text(self, text: str):
        """Update the recognized text display"""
        if self.recognized_text:
            self.recognized_text.value = text
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