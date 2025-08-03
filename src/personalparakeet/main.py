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

from personalparakeet.audio_engine import AudioEngine
from personalparakeet.ui.dictation_view import DictationView
from personalparakeet.core.clarity_engine import ClarityEngine
from personalparakeet.core.vad_engine import VoiceActivityDetector
from personalparakeet.core.injection_manager_enhanced import EnhancedInjectionManager
from personalparakeet.config import V3Config

# Setup comprehensive logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_dir = Path.home() / '.personalparakeet'
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_dir / 'personalparakeet.log', mode='w')  # Overwrite log each run
    ]
)
logger = logging.getLogger(__name__)


class PersonalParakeetV3:
    """Main application class for PersonalParakeet v3"""
    
    def __init__(self):
        self.config = V3Config()
        self.audio_engine = None
        self.dictation_view = None
        self.injection_manager = None
        self.is_running = False
        self.cleanup_registered = False
        
    async def initialize(self, page: ft.Page):
        """Initialize the application components"""
        try:
            # Register cleanup on page close
            if not self.cleanup_registered:
                self.register_cleanup(page)
                self.cleanup_registered = True
            
            # Configure page for floating transparent window
            await self.configure_window(page)
            logger.info("Window configuration completed")
            
            # Initialize audio engine with all components
            logger.info("Initializing audio engine...")
            self.audio_engine = AudioEngine(self.config, asyncio.get_event_loop())
            await self.audio_engine.initialize()
            logger.info("Audio engine initialized successfully")
            
            # Initialize text injection manager
            logger.info("Initializing text injection manager...")
            self.injection_manager = EnhancedInjectionManager()
            logger.info("Text injection manager initialized successfully")
            
            # Initialize dictation view
            logger.info("Creating dictation view...")
            self.dictation_view = DictationView(page, self.audio_engine, self.injection_manager, self.config)
            
            # Add UI to page
            logger.info("Building and adding UI to page...")
            ui_container = self.dictation_view.build()
            page.add(ui_container)
            logger.info("UI added to page successfully")
            
            # Start audio processing
            logger.info("Starting audio processing...")
            await self.audio_engine.start()
            self.is_running = True
            
            logger.info("PersonalParakeet v3 initialized successfully")
            
        except Exception as e:
            logger.error(f"CRITICAL: Failed to initialize PersonalParakeet v3: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception args: {e.args}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Attempt cleanup on failure
            await self.emergency_cleanup()
            raise
    
    async def configure_window(self, page: ft.Page):
        """Configure the main window properties"""
        # Add run_task helper for sync->async calls
        def run_task(coro):
            """Run an async task in the page's event loop"""
            try:
                asyncio.create_task(coro)
            except RuntimeError as e:
                logger.error(f"Failed to create task: {e}")
        
        page.run_task = run_task
        
        # Window configuration for floating dictation view
        page.window_always_on_top = True
        page.window_frameless = True
        page.window_resizable = False  # Disable resize to force exact size
        
        # Force exact window dimensions
        page.window_width = 450
        page.window_height = 350
        page.window_min_width = 450
        page.window_max_width = 450
        page.window_min_height = 350
        page.window_max_height = 350
        
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
    
    def register_cleanup(self, page: ft.Page):
        """Register cleanup handlers"""
        import atexit
        import signal
        
        # Register cleanup on normal exit
        atexit.register(self.emergency_cleanup_sync)
        
        # Register cleanup on signals (if available)
        try:
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            logger.info("Signal handlers registered")
        except (AttributeError, ValueError):
            logger.warning("Could not register signal handlers (may not be supported)")
    
    def signal_handler(self, signum, frame):
        """Handle termination signals"""
        logger.info(f"Received signal {signum}, initiating cleanup...")
        self.emergency_cleanup_sync()
        sys.exit(0)
    
    async def emergency_cleanup(self):
        """Emergency cleanup for async context"""
        logger.warning("Performing emergency cleanup...")
        try:
            self.is_running = False
            
            if self.audio_engine:
                await self.audio_engine.stop()
                
            # Force cleanup of any hanging processes
            import subprocess
            try:
                import os
                cleanup_script = os.path.join(os.path.dirname(__file__), "cleanup_processes.py")
                subprocess.run([
                    sys.executable, 
                    cleanup_script
                ], timeout=10, capture_output=True)
            except subprocess.TimeoutExpired:
                logger.warning("Cleanup script timed out")
                
        except Exception as e:
            logger.error(f"Error during emergency cleanup: {e}")
    
    def emergency_cleanup_sync(self):
        """Emergency cleanup for sync context"""
        try:
            import subprocess
            import os
            current_dir = Path(__file__).parent
            cleanup_script = current_dir / "cleanup_processes.py"
            subprocess.run([
                sys.executable, 
                str(cleanup_script)
            ], timeout=5, capture_output=True)
        except Exception as e:
            logger.error(f"Error during sync cleanup: {e}")


async def app_main(page: ft.Page):
    """Main Flet application entry point"""
    app = PersonalParakeetV3()
    
    # Handle window close event
    async def on_window_event(e):
        if e.data == "close":
            await app.shutdown()
            page.window_destroy()
    
    page.on_window_event = on_window_event
    
    try:
        # Initialize application
        await app.initialize(page)
        
        # Keep application running
        logger.info("PersonalParakeet v3 is ready!")
        logger.info("Use the UI controls or voice commands to interact")
        
    except RuntimeError as e:
        # Show critical error dialog for STT failures
        error_message = str(e)
        
        # Create error dialog
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Critical Error - STT Not Available", color=ft.colors.RED),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(
                        "PersonalParakeet cannot start without speech recognition.",
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Text(""),
                    ft.Text(error_message, size=12),
                ], scroll=ft.ScrollMode.AUTO),
                width=500,
                height=300,
            ),
            actions=[
                ft.TextButton("Exit", on_click=lambda e: page.window_destroy()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dlg
        dlg.open = True
        await page.update_async()
        
        # Log the error
        logger.error(f"Application cannot start: {e}")
        
    except Exception as e:
        # Show generic error dialog
        import traceback
        error_details = traceback.format_exc()
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Initialization Error", color=ft.colors.RED),
            content=ft.Container(
                content=ft.Column([
                    ft.Text(f"Failed to initialize: {str(e)}", weight=ft.FontWeight.BOLD),
                    ft.Text(""),
                    ft.Text("Details:", size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(error_details, size=10),
                ], scroll=ft.ScrollMode.AUTO),
                width=600,
                height=400,
            ),
            actions=[
                ft.TextButton("Exit", on_click=lambda e: page.window_destroy()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dlg
        dlg.open = True
        await page.update_async()
        
        logger.error(f"Application initialization failed: {e}")
        logger.error(error_details)


def main():
    """Entry point for running the Flet application"""
    logger.info("Starting PersonalParakeet v3 Flet Application")
    
    # Run the Flet app
    ft.app(
        target=app_main,
        view=ft.FLET_APP,  # Native desktop application
        port=0,  # Auto-assign available port to avoid conflicts
        assets_dir="assets"
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        import traceback
        logger.error(traceback.format_exc())