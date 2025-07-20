# Simple Parakeet Dictation - Direct Integration (FIXED)
# Connects: Working audio + NeMo + LocalAgreement + Keyboard output

import sounddevice as sd
import numpy as np
import nemo.collections.asr as nemo_asr
import torch
import keyboard
import time
import threading
from queue import Queue, Empty
import sys
import signal
import argparse
from typing import Optional, Callable, List

# Import your LocalAgreement logic
from .local_agreement import TranscriptionProcessor
from .audio_devices import AudioDeviceManager
from .config_manager import ConfigManager, PersonalParakeetConfig
from .text_injection import TextInjectionManager, ApplicationInfo, PlatformDetector
from .logger import setup_logger

logger = setup_logger(__name__)

class SimpleDictation:
    """A simplified dictation class for demonstration purposes."""

    def __init__(self, 
                 audio_input_callback: Optional[Callable[[], str]] = None,
                 stt_callback: Optional[Callable[[str], str]] = None,
                 device_index=None, device_name=None, agreement_threshold=1, chunk_duration=1.0, config_manager=None):
        """
        Initialize SimpleDictation with optional device selection and configuration
        
        Args:
            device_index: Specific device index to use
            device_name: Partial device name to search for (ignored if device_index provided)
            agreement_threshold: Number of consecutive agreements needed to commit text (1-5)
            chunk_duration: Audio processing chunk size in seconds (0.3-2.0)
            config_manager: ConfigManager instance (optional)
        """
        logger.info("Initializing Simple Parakeet Dictation...")
        
        # Configuration management
        self.config_manager = config_manager or ConfigManager()
        
        # If CLI args provided, use them; otherwise use config
        if agreement_threshold != 1 or chunk_duration != 1.0:
            # CLI args provided - use them directly
            self.agreement_threshold = max(1, min(5, agreement_threshold))
            self.chunk_duration = max(0.3, min(2.0, chunk_duration))
        else:
            # No CLI args - use config
            config = self.config_manager.get_config()
            self.agreement_threshold = getattr(config, 'agreement_threshold', 3)
            self.chunk_duration = config.chunk_duration
            self.max_pending_words = getattr(config, 'max_pending_words', 5)
            self.word_timeout = getattr(config, 'word_timeout', 2.0)
            self.position_tolerance = getattr(config, 'position_tolerance', 0.5)
            self.audio_level_threshold = getattr(config, 'audio_level_threshold', 0.01)
            logger.info(f"Using default configuration")
        
        # Audio device selection
        config = self.config_manager.get_config()
        effective_device_name = device_name  # Use provided device name
        self.device_index = self._select_audio_device(device_index, effective_device_name)
        
        # Audio settings (configurable for real-time dictation)
        self.sample_rate = config.sample_rate
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # State
        self.is_recording = False
        self.audio_queue = Queue()
        self.stream = None
        
        # Load Parakeet model (use larger 1.1B model for RTX 3090)
        logger.info("Loading Parakeet-TDT-1.1B model...")
        self.model = nemo_asr.models.ASRModel.from_pretrained(
            "nvidia/parakeet-tdt-1.1b",
            map_location="cuda"
        ).to(dtype=torch.float16)
        logger.info("Model loaded successfully")
        
        # LocalAgreement processor (configurable)
        self.processor = TranscriptionProcessor(agreement_threshold=self.agreement_threshold)
        self.processor.set_text_output_callback(self.output_text)
        
        # Audio processing thread
        self.processing_thread = None
        
        # Track injection failures for fallback display
        self.injection_failures = 0
        self.use_fallback_display = False
        
        # Initialize text injection manager
        self.text_injection_manager = TextInjectionManager()
        self.text_injection_manager.set_fallback_display(self._display_fallback_text)
    
    def _select_audio_device(self, device_index=None, device_name=None):
        """Select and validate audio input device"""
        # If specific index provided, validate it
        if device_index is not None:
            valid, msg = AudioDeviceManager.validate_device(device_index)
            if valid:
                logger.info(f"Using specified device: {msg}")
                return device_index
            else:
                logger.warning(f"{msg}")
                logger.warning("Falling back to device selection...")
        
        # If device name provided, try to find it
        if device_name:
            found_idx = AudioDeviceManager.find_device_by_name(device_name)
            if found_idx is not None:
                valid, msg = AudioDeviceManager.validate_device(found_idx)
                if valid:
                    logger.info(f"Found and using device: {msg}")
                    return found_idx
                else:
                    logger.warning(f"Found device but validation failed: {msg}")
            else:
                logger.warning(f"No device found matching '{device_name}'")
        
        # Try default device
        default_valid, default_msg = AudioDeviceManager.validate_device(None)
        if default_valid:
            logger.info(f"Using default device: {default_msg}")
            return None
        
        # If default doesn't work, show device list and let user choose
        logger.warning("Default device not available. Please select a device:")
        selected = AudioDeviceManager.select_device_interactive()
        
        if selected is None:
            raise RuntimeError("No audio input device selected")
            
        return selected
        
    def output_text(self, text):
        """Output committed text using the new text injection system"""
        logger.info(f"OUTPUT CALLBACK TRIGGERED: '{text}'")
        
        # Use the new text injection manager
        success = self.text_injection_manager.inject_text(text)
        
        if not success:
            # Track failures
            self.injection_failures += 1
            logger.warning(f"Text injection failed (attempt {self.injection_failures})")
        else:
            # Reset failure counter on success
            self.injection_failures = 0
    
    def _display_fallback_text(self, text):
        """Display text in console when injection fails"""
        logger.error(f"\n---\nINJECTION FAILED, TEXT TO INJECT:\n{text}\n---")
        
    def audio_callback(self, indata, frames, time, status):
        """Audio input callback with error handling - queues chunks for processing"""
        if status:
            logger.warning(f"Audio status: {status}")
            
        if self.is_recording:
            try:
                # Convert to float32 and add to queue
                audio_chunk = indata[:, 0].astype(np.float32)
                
                # Don't overflow the queue
                if self.audio_queue.qsize() < 50:  # Limit queue size
                    self.audio_queue.put(audio_chunk.copy())
                else:
                    logger.warning("Audio queue full, dropping chunk")
                    
            except Exception as e:
                logger.error(f"Audio callback error: {type(e).__name__}: {str(e)}")
    
    def process_audio_loop(self):
        """Background thread that processes audio chunks with robust error handling"""
        logger.info("Audio processing thread started")
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.is_recording:
            try:
                # Get audio chunk (blocking with timeout)
                audio_chunk = self.audio_queue.get(timeout=0.5)
                
                # Check if we have enough audio (avoid processing silence)
                max_level = np.max(np.abs(audio_chunk))
                audio_threshold = getattr(self, 'audio_level_threshold', 0.01)
                if max_level < audio_threshold:  # Very quiet, skip
                    continue
                
                logger.debug(f"Processing audio chunk (level: {max_level:.3f})")
                
                # Transcribe with Parakeet
                try:
                    with torch.inference_mode():
                        result = self.model.transcribe([audio_chunk])
                        raw_text = result[0].text if result and result[0].text else ""
                except torch.cuda.OutOfMemoryError:
                    logger.error("GPU out of memory! Clearing cache...")
                    torch.cuda.empty_cache()
                    consecutive_errors += 1
                    continue
                except Exception as e:
                    logger.error(f"Transcription error: {type(e).__name__}: {str(e)}")
                    consecutive_errors += 1
                    continue
                
                if raw_text.strip():
                    logger.info(f"Raw transcription: '{raw_text}'")
                    
                    # Process through LocalAgreement with error handling
                    try:
                        state = self.processor.process_transcription(raw_text)
                        
                        # Display current state
                        if state.committed or state.pending:
                            logger.info(f"Committed: '{state.committed}' | Pending: '{state.pending}'")
                        
                        # Reset error counter on success
                        consecutive_errors = 0
                        
                    except Exception as e:
                        logger.error(f"LocalAgreement processing error: {type(e).__name__}: {str(e)}")
                        consecutive_errors += 1
                
            except Empty:
                # Queue timeout is normal when no audio is coming in
                continue
            except Exception as e:
                if self.is_recording:  # Only show errors if we're still supposed to be recording
                    logger.error(f"Processing error: {type(e).__name__}: {str(e)}")
                    consecutive_errors += 1
                    
            # Check if we've hit too many consecutive errors
            if consecutive_errors >= max_consecutive_errors:
                logger.error(f"Too many consecutive errors ({consecutive_errors}). Stopping audio processing...")
                self.stop_dictation()
                break
                
        logger.info("Audio processing thread stopped")
    
    def start_dictation(self):
        """Start dictation (F4 key) with error handling"""
        if self.is_recording:
            logger.warning("Already recording!")
            return
            
        logger.info("Starting dictation...")
        
        try:
            # Clear the audio queue before starting
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except Empty:
                    break
                    
            self.is_recording = True
            
            # Start audio processing thread
            self.processing_thread = threading.Thread(target=self.process_audio_loop, daemon=True)
            self.processing_thread.start()
            
            # Start audio stream with error handling
            try:
                self.stream = sd.InputStream(
                    device=self.device_index,
                    samplerate=self.sample_rate,
                    channels=1,
                    callback=self.audio_callback,
                    blocksize=self.chunk_size
                )
                self.stream.start()
                
                logger.info("Dictation active! Speak now...")
                logger.info("Text will appear where your cursor is")
                logger.info("Press F4 again to stop")
                
            except Exception as e:
                logger.error(f"Failed to start audio stream: {type(e).__name__}: {str(e)}")
                self.is_recording = False
                raise
                
        except Exception as e:
            logger.error(f"Failed to start dictation: {type(e).__name__}: {str(e)}")
            self.is_recording = False
    
    def stop_dictation(self):
        """Stop dictation (F4 key) with graceful shutdown"""
        if not self.is_recording:
            logger.warning("Not currently recording!")
            return
            
        logger.info("Stopping dictation...")
        self.is_recording = False
        
        # Stop audio stream
        if hasattr(self, 'stream') and self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                logger.warning(f"Error stopping audio stream: {type(e).__name__}: {str(e)}")
            finally:
                self.stream = None
        
        # Wait for processing thread to finish
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5.0)
            if self.processing_thread.is_alive():
                logger.warning("Processing thread did not stop cleanly")
        
        # Process any remaining pending text with error handling
        try:
            if self.processor.buffer.pending_words:
                pending_text = " ".join(self.processor.buffer.pending_words)
                logger.info(f"Flushing pending text: '{pending_text}'")
                self.output_text(pending_text)  # Use our error-handled output method
        except Exception as e:
            logger.error(f"Error flushing pending text: {type(e).__name__}: {str(e)}")
        
        # Clear the audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except Empty:
                break
        
        logger.info("Dictation stopped")
    
    def toggle_dictation(self):
        """Toggle dictation on/off"""
        if self.is_recording:
            self.stop_dictation()
        else:
            self.start_dictation()
    
    def cleanup(self):
        """Comprehensive cleanup of all resources"""
        logger.info("Performing cleanup...")
        
        # Stop dictation if running
        if self.is_recording:
            self.stop_dictation()
        
        # Clear any remaining GPU memory
        try:
            if hasattr(self, 'model'):
                del self.model
                torch.cuda.empty_cache()
                logger.info("GPU memory cleared")
        except Exception as e:
            logger.warning(f"Error clearing GPU memory: {e}")
        
        # Close any remaining streams
        if hasattr(self, 'stream') and self.stream:
            try:
                self.stream.abort()
                self.stream.close()
            except:
                pass
        
        logger.info("Cleanup completed")
    
    def switch_profile(self, profile_name: str) -> bool:
        """Switch configuration profile at runtime"""
        logger.warning("Profile switching not yet implemented")
        return False
    
    def _apply_configuration_changes(self) -> None:
        """Apply configuration changes without restart"""
        config = self.config_manager.get_config()
        
        # Update audio processing parameters
        self.chunk_duration = config.chunk_duration
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        self.audio_level_threshold = getattr(config, 'audio_level_threshold', 0.01)
        
        # Update processor settings
        self.agreement_threshold = getattr(config, 'agreement_threshold', 3)
        self.processor.set_agreement_threshold(self.agreement_threshold)
        
        # Update other LocalAgreement parameters if the processor supports them
        if hasattr(self.processor, 'set_max_pending_words'):
            self.processor.set_max_pending_words(getattr(config, 'max_pending_words', 5))
        if hasattr(self.processor, 'set_timeout_seconds'):
            self.processor.set_timeout_seconds(getattr(config, 'word_timeout', 2.0))
        if hasattr(self.processor, 'set_position_tolerance'):
            self.processor.set_position_tolerance(getattr(config, 'position_tolerance', 0.5))
        
        logger.info(f"Applied configuration updates")
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available configuration profiles"""
        return []  # Profile support not yet implemented
    
    def get_current_profile(self) -> PersonalParakeetConfig:
        """Get the current active profile"""
        return self.config_manager.get_config()

def main(device_index=None, device_name=None, list_devices=False, agreement_threshold=1, chunk_duration=1.0, profile=None, list_profiles=False):
    """Main entry point with comprehensive error handling"""
    
    # Initialize configuration manager first
    config_manager = ConfigManager()
    
    # Just list devices if requested
    if list_devices:
        AudioDeviceManager.print_input_devices()
        return
    
    # Just list profiles if requested
    if list_profiles:
        logger.info("Profile support not yet implemented")
        return
    
    # Switch profile if requested
    if profile:
        logger.warning("Profile switching not yet implemented")
        if False:
            logger.error(f"Failed to switch to profile: {profile}")
            return
    
    logger.info("Simple Parakeet Dictation System")
    logger.info("=" * 50)
    
    dictation = None
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.warning("Signal received, shutting down gracefully...")
        if dictation:
            dictation.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create dictation system with error handling
        logger.info("Initializing system...")
        dictation = SimpleDictation(
            device_index=device_index, 
            device_name=device_name,
            agreement_threshold=agreement_threshold,
            chunk_duration=chunk_duration,
            config_manager=config_manager
        )
        
        # Set up hotkeys from configuration
        logger.info("Setting up hotkeys...")
        config = config_manager.get_config()
        toggle_hotkey = config.toggle_hotkey
        keyboard.add_hotkey(toggle_hotkey.lower(), dictation.toggle_dictation)
        logger.info(f"Hotkey registered: {toggle_hotkey} to start/stop dictation")
        
        logger.info("READY TO USE:")
        logger.info("1. Click in any text field (Notepad, browser, etc.)")
        logger.info(f"2. Press {toggle_hotkey} to start dictation")
        logger.info("3. Speak clearly")
        logger.info("4. Watch text appear with LocalAgreement buffering")
        logger.info(f"5. Press {toggle_hotkey} again to stop")
        logger.info("6. Press Ctrl+C to quit")
        logger.info(f"Waiting for {toggle_hotkey}...")
        
        # Keep running until Ctrl+C
        keyboard.wait('ctrl+c')
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        
    except sd.PortAudioError as e:
        logger.error(f"Audio device error: {e}")
        logger.error("Check if microphone is connected")
        logger.error("Try closing other applications using the microphone")
        logger.error("Try restarting the application")
        logger.error("Check Windows sound settings")
        
    except torch.cuda.CudaError as e:
        logger.error(f"CUDA/GPU error: {e}")
        logger.error("Check if NVIDIA drivers are installed")
        logger.error("Try restarting the application")
        logger.error("Check GPU memory usage with nvidia-smi")
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Check if all dependencies are installed")
        logger.error("Run: pip install -r requirements.txt")
        
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
    finally:
        # Cleanup
        logger.info("Cleaning up...")
        
        # Comprehensive cleanup
        if dictation:
            try:
                dictation.cleanup()
            except Exception as e:
                logger.warning(f"Cleanup error: {e}")
        
        # Remove hotkey
        try:
            keyboard.remove_all_hotkeys()
        except:
            pass
            
        logger.info("Goodbye!")


def cli():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="PersonalParakeet - Real-time dictation with NVIDIA Parakeet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Use default audio device
  %(prog)s --list-devices     # List available devices
  %(prog)s --list-profiles    # List available configuration profiles
  %(prog)s --device 2         # Use device index 2
  %(prog)s --device-name "Blue Yeti"  # Use device by name
  %(prog)s --profile accurate_document  # Use accurate document mode
  %(prog)s --agreement-threshold 3    # More accurate mode
  %(prog)s --chunk-duration 0.5       # Faster processing
        """
    )
    
    parser.add_argument(
        '--device', '-d',
        type=int,
        help='Audio device index to use'
    )
    
    parser.add_argument(
        '--device-name', '-n',
        type=str,
        help='Partial name of audio device to use'
    )
    
    parser.add_argument(
        '--list-devices', '-l',
        action='store_true',
        help='List available audio input devices and exit'
    )
    
    parser.add_argument(
        '--agreement-threshold', '-t',
        type=int,
        default=1,
        help='Number of consecutive agreements needed to commit text (1-5, default: 1)'
    )
    
    parser.add_argument(
        '--chunk-duration', '-c',
        type=float,
        default=1.0,
        help='Audio processing chunk size in seconds (0.3-2.0, default: 1.0)'
    )
    
    parser.add_argument(
        '--profile', '-p',
        type=str,
        help='Configuration profile to use (fast_conversation, balanced, accurate_document, low_latency)'
    )
    
    parser.add_argument(
        '--list-profiles',
        action='store_true',
        help='List available configuration profiles and exit'
    )
    
    args = parser.parse_args()
    
    # Run main with arguments
    main(
        device_index=args.device,
        device_name=args.device_name,
        list_devices=args.list_devices,
        agreement_threshold=args.agreement_threshold,
        chunk_duration=args.chunk_duration,
        profile=args.profile,
        list_profiles=args.list_profiles
    )

if __name__ == "__main__":
    cli()
