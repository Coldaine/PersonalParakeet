#!/usr/bin/env python3
"""
DictationView - Main Flet UI component for PersonalParakeet v3
Replaces React/Tauri components with native Flet widgets
"""

import asyncio
import logging
import time
from typing import Optional

import flet as ft
from flet import Colors, Icons

from ui.components import StatusIndicator, ControlPanel, ConfidenceBar, VADIndicator
from ui.theme import get_dictation_theme
from core.clarity_engine import CorrectionResult
from config import V3Config

logger = logging.getLogger(__name__)


class DictationView:
    """
    Main dictation view UI component
    Provides floating transparent window with real-time transcription display
    """
    
    def __init__(self, page: ft.Page, audio_engine, injection_manager, config: V3Config):
        self.page = page
        self.audio_engine = audio_engine
        self.injection_manager = injection_manager
        self.config = config
        
        # UI state
        self.text = ""
        self.corrected_text = ""
        self.confidence = 0.0
        self.is_listening = False
        self.is_connected = True
        self.clarity_enabled = True
        self.vad_status = {
            'is_speech': False,
            'rms_energy': 0.0,
            'is_speaking': False,
            'pause_duration': 0.0
        }
        self.last_update_type = "none"
        self.correction_info = None
        
        # UI components
        self.status_indicator = None
        self.vad_indicator = None
        self.control_panel = None
        self.text_display = None
        self.confidence_bar = None
        self.cursor_visible = True
        
        # Setup callbacks for audio engine
        self._setup_audio_callbacks()
        
        # Start cursor blinking
        self._start_cursor_blink()
    
    def _setup_audio_callbacks(self):
        """Setup callbacks for audio engine updates"""
        self.audio_engine.set_raw_transcription_callback(self._on_raw_transcription)
        self.audio_engine.set_corrected_transcription_callback(self._on_corrected_transcription)
        self.audio_engine.set_pause_detected_callback(self._on_pause_detected)
        self.audio_engine.set_vad_status_callback(self._on_vad_status)
        self.audio_engine.set_error_callback(self._on_error)
    
    def _start_cursor_blink(self):
        """Start cursor blinking animation"""
        async def blink_cursor():
            while True:
                await asyncio.sleep(0.5)
                self.cursor_visible = not self.cursor_visible
                if self.text_display:
                    await self._update_text_display()
        
        # Start cursor blinking task
        asyncio.create_task(blink_cursor())
    
    def build(self) -> ft.Container:
        """Build and return the main UI container"""
        theme = get_dictation_theme()
        
        # Create UI components
        self.status_indicator = StatusIndicator(self.is_connected, self.is_listening)
        self.vad_indicator = VADIndicator(self.vad_status)
        self.control_panel = ControlPanel(
            self.clarity_enabled,
            False,  # command mode not yet implemented
            self._on_toggle_clarity,
            self._on_commit_text,
            self._on_clear_text
        )
        
        # Text display area
        self.text_display = ft.Container(
            content=ft.Column([
                self._create_primary_text_display(),
                self._create_correction_info_display(),
            ], spacing=5),
            padding=ft.padding.all(15),
            expand=True
        )
        
        # Confidence bar
        self.confidence_bar = ConfidenceBar(self.confidence)
        
        # Main container with glass morphism effect
        main_container = ft.Container(
            content=ft.Column([
                # Header with status and controls
                ft.Row([
                    self.status_indicator.build(),
                    self.vad_indicator.build(),
                    ft.Container(expand=True),  # Spacer
                    self.control_panel.build(),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                # Main content area
                self.text_display,
                
                # Footer with confidence
                self.confidence_bar.build(),
            ], spacing=10),
            
            # Glass morphism styling
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
            border_radius=15,
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
            padding=ft.padding.all(20),
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            
            # Set fixed size to match window
            width=430,  # Slightly smaller than window to account for padding
            height=330,
        )
        
        return main_container
    
    def _create_primary_text_display(self) -> ft.Text:
        """Create the main text display widget"""
        display_text = self.corrected_text or self.text
        if self.cursor_visible and display_text:
            display_text += "|"
        
        return ft.Text(
            display_text or "Speak to start transcription...",
            size=18,
            weight=ft.FontWeight.W_400,
            color=ft.Colors.WHITE if display_text else ft.Colors.GREY_400,
            text_align=ft.TextAlign.LEFT,
            selectable=True
        )
    
    def _create_correction_info_display(self) -> ft.Container:
        """Create correction information display"""
        if not self.correction_info or not self.correction_info.corrections_made:
            return ft.Container()
        
        corrections_text = f"{len(self.correction_info.corrections_made)} corrections"
        timing_text = f"{self.correction_info.processing_time_ms:.0f}ms"
        
        return ft.Container(
            content=ft.Row([
                ft.Text(
                    corrections_text,
                    size=12,
                    color=ft.Colors.AMBER_300,
                ),
                ft.Text(
                    timing_text,
                    size=12,
                    color=ft.Colors.GREEN_300 if self.correction_info.processing_time_ms < 150 else ft.Colors.ORANGE_300,
                )
            ], spacing=10),
            visible=bool(self.correction_info and self.correction_info.corrections_made)
        )
    
    async def _update_text_display(self):
        """Update the text display with current content"""
        if self.text_display:
            # Update primary text
            primary_text = self.text_display.content.controls[0]
            display_text = self.corrected_text or self.text
            if self.cursor_visible and display_text:
                display_text += "|"
            
            primary_text.value = display_text or "Speak to start transcription..."
            primary_text.color = ft.Colors.WHITE if display_text else ft.Colors.GREY_400
            
            self.page.update()
    
    async def _update_ui_state(self):
        """Update all UI components to reflect current state"""
        if self.status_indicator:
            self.status_indicator.update_state(self.is_connected, self.is_listening)
        
        if self.vad_indicator:
            self.vad_indicator.update_status(self.vad_status)
        
        if self.control_panel:
            self.control_panel.update_state(self.clarity_enabled, False)  # command mode TODO
        
        if self.confidence_bar:
            self.confidence_bar.update_confidence(self.confidence)
        
        await self._update_text_display()
        self.page.update()
    
    # Event handlers
    
    def _on_pan_update(self, e: ft.DragUpdateEvent):
        """Handle window dragging"""
        # TODO: Implement window dragging
        # This may require native window management
        pass
    
    def _on_toggle_clarity(self):
        """Handle clarity toggle button (sync)"""
        self.clarity_enabled = not self.clarity_enabled
        self.audio_engine.set_clarity_enabled(self.clarity_enabled)
        asyncio.create_task(self._update_ui_state())
        logger.info(f"Clarity {'enabled' if self.clarity_enabled else 'disabled'}")
    
    def _on_commit_text(self):
        """Handle commit text button (sync)"""
        if self.text or self.corrected_text:
            final_text = self.corrected_text or self.text
            logger.info(f"Committing text: '{final_text.strip()}'")
            
            # Inject text asynchronously
            if self.injection_manager:
                asyncio.create_task(self._inject_text_async(final_text.strip()))
            
            asyncio.create_task(self._clear_current_text())
    
    def _on_clear_text(self):
        """Handle clear text button (sync)"""
        asyncio.create_task(self._clear_current_text())
    
    async def _clear_current_text(self):
        """Clear current text and reset state"""
        self.text = ""
        self.corrected_text = ""
        self.confidence = 0.0
        self.correction_info = None
        self.last_update_type = "cleared"
        
        self.audio_engine.clear_current_text()
        
        await self._update_ui_state()
        logger.info("Text cleared")
    
    # Audio engine callbacks
    
    async def _on_raw_transcription(self, text: str):
        """Handle raw transcription from STT"""
        self.text = text
        self.last_update_type = "raw"
        self.confidence = 0.8  # Default confidence for raw text
        
        await self._update_ui_state()
        logger.debug(f"Raw transcription: '{text}'")
    
    async def _on_corrected_transcription(self, result: CorrectionResult):
        """Handle corrected transcription from Clarity Engine"""
        self.corrected_text = result.corrected_text
        self.confidence = result.confidence
        self.correction_info = result
        self.last_update_type = "corrected"
        
        await self._update_ui_state()
        logger.debug(f"Corrected transcription: '{result.corrected_text}'")
    
    async def _on_pause_detected(self, pause_duration: float, text: str):
        """Handle pause detection from VAD"""
        logger.info(f"Pause detected ({pause_duration:.2f}s), auto-committing")
        
        # Auto-commit on pause
        if text.strip():
            final_text = self.corrected_text or text
            logger.info(f"Auto-committing: '{final_text.strip()}'")
            
            # Inject text into active application
            if self.injection_manager:
                await self._inject_text_async(final_text.strip())
            
            await self._clear_current_text()
    
    async def _on_vad_status(self, vad_status: dict):
        """Handle VAD status updates"""
        self.vad_status = vad_status
        
        # Update VAD indicator
        if self.vad_indicator:
            self.vad_indicator.update_status(vad_status)
            self.page.update()
    
    async def _on_error(self, error_message: str):
        """Handle error messages from audio engine"""
        logger.error(f"Audio engine error: {error_message}")
        
        # TODO: Show error in UI
        # For now, just log it
    
    async def _inject_text_async(self, text: str):
        """Inject text asynchronously using the injection manager"""
        if not text or not text.strip():
            logger.warning("Attempted to inject empty text")
            return
        
        try:
            # Run injection in a thread pool to avoid blocking the UI
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, 
                self.injection_manager.inject_text, 
                text.strip()
            )
            logger.info(f"Text injection completed: '{text.strip()[:50]}...'")
        except Exception as e:
            logger.error(f"Text injection failed: {e}")