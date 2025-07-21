#!/usr/bin/env python3
"""
PersonalParakeet v3 - Flet Single-Process Architecture
Main entry point for the dictation system with integrated UI
"""

import asyncio
import logging
import threading
import sys
from pathlib import Path

import flet as ft

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from audio_engine import AudioEngine
from ui.dictation_view import DictationView
from core.stt_processor import STTProcessor
from core.clarity_engine import ClarityEngine 
from core.vad_engine import VoiceActivityDetector
from config import V3Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PersonalParakeetV3:
    """Main application class for PersonalParakeet v3"""
    
    def __init__(self):
        self.config = V3Config()
        self.audio_engine = None
        self.dictation_view = None
        self.is_running = False
        
    async def initialize(self, page: ft.Page):
        """Initialize the application components"""
        try:
            # Configure page for floating transparent window
            await self.configure_window(page)
            
            # Initialize audio engine with all components
            self.audio_engine = AudioEngine(self.config, asyncio.get_event_loop())
            await self.audio_engine.initialize()
            
            # Initialize dictation view
            self.dictation_view = DictationView(page, self.audio_engine, self.config)
            
            # Add UI to page
            page.add(self.dictation_view.build())
            
            # Start audio processing
            await self.audio_engine.start()
            self.is_running = True
            
            logger.info("PersonalParakeet v3 initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PersonalParakeet v3: {e}")
            raise
    
    async def configure_window(self, page: ft.Page):
        """Configure the main window properties"""
        # Window configuration for floating dictation view
        page.window_always_on_top = True
        page.window_frameless = True
        page.window_resizable = True
        page.window_width = self.config.window.default_width
        page.window_height = self.config.window.default_height
        page.window_opacity = self.config.window.opacity
        
        # Set transparent background
        page.bgcolor = ft.Colors.TRANSPARENT
        page.theme_mode = ft.ThemeMode.DARK
        
        # Window title
        page.title = "PersonalParakeet v3"
        
        # Center window on screen initially
        # page.window_center()  # Not available in this Flet version
        
        logger.info("Window configured for floating transparent UI")
    
    async def shutdown(self):
        """Clean shutdown of all components"""
        logger.info("Shutting down PersonalParakeet v3...")
        self.is_running = False
        
        if self.audio_engine:
            await self.audio_engine.stop()
        
        logger.info("Shutdown complete")


async def main(page: ft.Page):
    """Main Flet application entry point"""
    app = PersonalParakeetV3()
    
    # Handle window close event
    async def on_window_event(e):
        if e.data == "close":
            await app.shutdown()
            page.window_destroy()
    
    page.on_window_event = on_window_event
    
    # Initialize application
    await app.initialize(page)
    
    # Keep application running
    logger.info("PersonalParakeet v3 is ready!")
    logger.info("Use the UI controls or voice commands to interact")


def run_app():
    """Entry point for running the Flet application"""
    logger.info("Starting PersonalParakeet v3 Flet Application")
    
    # Run the Flet app
    ft.app(
        target=main,
        view=ft.FLET_APP,  # Native desktop application
        port=8551,  # Custom port to avoid conflicts
        assets_dir="assets"
    )


if __name__ == "__main__":
    try:
        run_app()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        import traceback
        logger.error(traceback.format_exc())