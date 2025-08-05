#!/usr/bin/env python3
"""
PersonalParakeet v3 - Flet Single-Process Architecture
Main entry point for the dictation system with integrated UI
"""

import asyncio
import logging
import threading
import sys
import os
from pathlib import Path

# import flet as ft  # REMOVED - replaced with Rust UI

from personalparakeet.audio_engine import AudioEngine
from personalparakeet.ui.dictation_view import DictationView
from personalparakeet.core.clarity_engine import ClarityEngine
from personalparakeet.core.vad_engine import VoiceActivityDetector
from personalparakeet.core.injection_manager_enhanced import EnhancedInjectionManager
from personalparakeet.core.thought_linker import ThoughtLinker
from personalparakeet.core.thought_linking_integration import ThoughtLinkingIntegration
from personalparakeet.config import V3Config

# Setup comprehensive logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_dir = Path.home() / '.personalparakeet'
log_dir.mkdir(exist_ok=True)

# Configure logging based on environment
if os.environ.get('PERSONALPARAKEET_BACKGROUND'):
    # Background mode - only file logging
    handlers = [
        logging.FileHandler(log_dir / 'personalparakeet.log', mode='a')
    ]
else:
    # Normal mode - both console and file
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(log_dir / 'personalparakeet.log', mode='w')  # Overwrite log each run
    ]

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=handlers
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
        
    async def initialize(self, rust_ui):
        """Initialize the application components"""
        try:
            # Register cleanup
            if not self.cleanup_registered:
                self.register_cleanup(rust_ui)
                self.cleanup_registered = True
            
            # Configure window for floating transparent UI
            await self.configure_window(rust_ui)
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
            
            # Initialize thought linker
            logger.info("Initializing thought linker...")
            self.thought_linker = ThoughtLinker(
                enabled=self.config.thought_linking.enabled,
                similarity_threshold=self.config.thought_linking.similarity_threshold,
                timeout_threshold=self.config.thought_linking.timeout_threshold,
                cursor_movement_threshold=self.config.thought_linking.cursor_movement_threshold
            )
            logger.info(f"Thought linker initialized (enabled={self.thought_linker.enabled})")
            
            # Initialize thought linking integration
            logger.info("Initializing thought linking integration...")
            self.thought_linking_integration = ThoughtLinkingIntegration(
                self.thought_linker,
                self.injection_manager
            )
            logger.info("Thought linking integration initialized successfully")
            
            # Connect audio engine callbacks to text injection
            logger.info("Connecting audio engine callbacks...")
            
            # Connect audio engine callbacks to Rust UI AND text injection
            def handle_raw_transcription(text: str):
                rust_ui.update_text(text, "APPEND_WITH_SPACE")
                if text and text.strip():
                    success = self.injection_manager.inject_text(text)
                    if success:
                        logger.info(f"Injected text: {text}")
                    else:
                        logger.warning(f"Failed to inject text: {text}")
            
            def handle_corrected_transcription(result):
                if hasattr(result, 'corrected_text'):
                    text = result.corrected_text
                else:
                    text = str(result)
                rust_ui.update_text(text, "REPLACE")
            
            self.audio_engine.on_raw_transcription = handle_raw_transcription
            self.audio_engine.on_corrected_transcription = handle_corrected_transcription
            self.audio_engine.on_pause_detected = lambda: rust_ui.update_status("Pause detected", "yellow")
            self.audio_engine.on_vad_status = lambda active: rust_ui.set_recording(active)
            self.audio_engine.on_error = lambda error: rust_ui.show_error(str(error))
            logger.info("Audio engine callbacks connected")
            
            logger.info("Rust UI callbacks connected successfully")
            
            # Start audio processing
            logger.info("Starting audio processing...")
            await self.audio_engine.start()
            self.is_running = True
            
            # Log thought linking status
            logger.info(f"Thought linking status: enabled={self.config.thought_linking.enabled}")
            logger.info(f"Thought linker instance created: enabled={self.thought_linker.enabled}")
            
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
    
    async def configure_window(self, rust_ui):
        """Configure window properties for floating UI"""
        async def run_task():
            try:
                await asyncio.sleep(0.1)  # Small delay to ensure UI is ready
                logger.info("Configuring window properties...")
                rust_ui.set_window_properties(transparent=True, always_on_top=False)
                logger.info("Window configuration completed")
            except Exception as e:
                logger.error(f"Error configuring window: {e}")
        
        asyncio.create_task(run_task())
    
    async def shutdown(self):
        """Clean shutdown of all components"""
        logger.info("Shutting down PersonalParakeet v3...")
        self.is_running = False
        
        if self.audio_engine:
            await self.audio_engine.stop()
        
        logger.info("Shutdown complete")
    
    def register_cleanup(self, rust_ui):
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


async def app_main():
    """Main application entry point using Rust UI"""
    app = PersonalParakeetV3()
    
    try:
        # Initialize Rust UI
        import personalparakeet_ui
        rust_ui = personalparakeet_ui.GuiController()
        
        # Initialize application with Rust UI BEFORE running GUI
        await app.initialize(rust_ui)
        
        if not app.audio_engine.stt_processor:
            logger.error("STT processor not available")
            rust_ui.show_error(
                "Speech-to-Text (STT) processor could not be initialized. "
                "This is likely due to missing NVIDIA GPU, CUDA drivers, "
                "insufficient GPU memory, or missing model files. "
                "Please check the logs for more details."
            )
            return
        
        # Configure window properties
        await app.configure_window(rust_ui)
        
        # Register cleanup handlers
        app.register_cleanup(rust_ui)
        
        # Start audio processing
        await app.audio_engine.start()
        logger.info("PersonalParakeet v3 is ready!")
        logger.info("Use the UI controls or voice commands to interact")
        
        # Run the GUI on main thread (blocking call) - this should be LAST
        rust_ui.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise


def main():
    """Entry point for running the Rust + egui application"""
    logger.info("Starting PersonalParakeet v3 Rust + egui Application")
    
    # Run the application with Rust UI
    import asyncio
    asyncio.run(app_main())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        import traceback
        logger.error(traceback.format_exc())
