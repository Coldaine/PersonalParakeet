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

# Import your LocalAgreement logic
from .local_agreement import TranscriptionProcessor
from .audio_devices import AudioDeviceManager

class SimpleDictation:
    def __init__(self, device_index=None, device_name=None):
        """
        Initialize SimpleDictation with optional device selection
        
        Args:
            device_index: Specific device index to use
            device_name: Partial device name to search for (ignored if device_index provided)
        """
        print("🔧 Initializing Simple Parakeet Dictation...")
        
        # Audio device selection
        self.device_index = self._select_audio_device(device_index, device_name)
        
        # Audio settings (optimized for real-time dictation)
        self.sample_rate = 16000
        self.chunk_duration = 1.0  # 1 second chunks for more responsive processing
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # State
        self.is_recording = False
        self.audio_queue = Queue()
        self.stream = None
        
        # Load Parakeet model (use larger 1.1B model for RTX 3090)
        print("📡 Loading Parakeet-TDT-1.1B model...")
        self.model = nemo_asr.models.ASRModel.from_pretrained(
            "nvidia/parakeet-tdt-1.1b",
            map_location="cuda"
        ).to(dtype=torch.float16)
        print("✅ Model loaded successfully")
        
        # LocalAgreement processor (your innovation!)
        # Very low threshold for testing - we can tune this up later
        self.processor = TranscriptionProcessor(agreement_threshold=1)
        self.processor.set_text_output_callback(self.output_text)
        
        # Audio processing thread
        self.processing_thread = None
        
        # Track injection failures for fallback display
        self.injection_failures = 0
        self.use_fallback_display = False
    
    def _select_audio_device(self, device_index=None, device_name=None):
        """Select and validate audio input device"""
        # If specific index provided, validate it
        if device_index is not None:
            valid, msg = AudioDeviceManager.validate_device(device_index)
            if valid:
                print(f"🎤 Using specified device: {msg}")
                return device_index
            else:
                print(f"⚠️  {msg}")
                print("   Falling back to device selection...")
        
        # If device name provided, try to find it
        if device_name:
            found_idx = AudioDeviceManager.find_device_by_name(device_name)
            if found_idx is not None:
                valid, msg = AudioDeviceManager.validate_device(found_idx)
                if valid:
                    print(f"🎤 Found and using device: {msg}")
                    return found_idx
                else:
                    print(f"⚠️  Found device but validation failed: {msg}")
            else:
                print(f"⚠️  No device found matching '{device_name}'")
        
        # Try default device
        default_valid, default_msg = AudioDeviceManager.validate_device(None)
        if default_valid:
            print(f"🎤 Using default device: {default_msg}")
            return None
        
        # If default doesn't work, show device list and let user choose
        print("\n⚠️  Default device not available. Please select a device:")
        selected = AudioDeviceManager.select_device_interactive()
        
        if selected is None:
            raise RuntimeError("No audio input device selected")
            
        return selected
        
    def output_text(self, text):
        """Output committed text via keyboard with thread safety"""
        print(f"📝 OUTPUT CALLBACK TRIGGERED: '{text}'")
        
        # Check if we're on the main thread
        import threading
        current_thread = threading.current_thread()
        is_main_thread = current_thread is threading.main_thread()
        
        if not is_main_thread:
            print(f"⚠️  Running in thread: {current_thread.name}")
        
        try:
            # Add small delay to ensure focus remains on target window
            time.sleep(0.05)
            
            # Try keyboard.write with better error handling
            keyboard.write(text + " ")  # Add space after each word/phrase
            print(f"✅ Successfully wrote text: '{text}'")
            
        except AttributeError as e:
            print(f"❌ Keyboard module error (likely threading issue): {e}")
            # Try alternative method using keyboard.press and release
            try:
                for char in text + " ":
                    keyboard.press_and_release(char)
                    time.sleep(0.01)  # Small delay between keystrokes
                print(f"✅ Successfully wrote text using press_and_release")
            except Exception as fallback_error:
                print(f"❌ Fallback method also failed: {fallback_error}")
                
        except Exception as e:
            print(f"❌ Failed to write text: {type(e).__name__}: {e}")
            # Log additional debug info
            print(f"   Text length: {len(text)}")
            print(f"   Text content: {repr(text)}")
            
            # Track failures and switch to fallback if needed
            self.injection_failures += 1
            if self.injection_failures >= 3 and not self.use_fallback_display:
                print("⚠️  Multiple injection failures detected. Switching to console display mode.")
                self.use_fallback_display = True
            
            # Fallback: Display text in console
            if self.use_fallback_display:
                self._display_fallback_text(text)
    
    def _display_fallback_text(self, text):
        """Display text in console when injection fails"""
        print("\n" + "=" * 60)
        print("📝 DICTATED TEXT (copy/paste manually):")
        print("=" * 60)
        print(text)
        print("=" * 60 + "\n")
        
    def audio_callback(self, indata, frames, time, status):
        """Audio input callback with error handling - queues chunks for processing"""
        if status:
            print(f"⚠️  Audio status: {status}")
            
        if self.is_recording:
            try:
                # Convert to float32 and add to queue
                audio_chunk = indata[:, 0].astype(np.float32)
                
                # Don't overflow the queue
                if self.audio_queue.qsize() < 50:  # Limit queue size
                    self.audio_queue.put(audio_chunk.copy())
                else:
                    print("⚠️  Audio queue full, dropping chunk")
                    
            except Exception as e:
                print(f"❌ Audio callback error: {type(e).__name__}: {str(e)}")
    
    def process_audio_loop(self):
        """Background thread that processes audio chunks with robust error handling"""
        print("🎤 Audio processing thread started")
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.is_recording:
            try:
                # Get audio chunk (blocking with timeout)
                audio_chunk = self.audio_queue.get(timeout=0.5)
                
                # Check if we have enough audio (avoid processing silence)
                max_level = np.max(np.abs(audio_chunk))
                if max_level < 0.01:  # Very quiet, skip
                    continue
                
                print(f"🔊 Processing audio chunk (level: {max_level:.3f})")
                
                # Transcribe with Parakeet
                try:
                    with torch.inference_mode():
                        result = self.model.transcribe([audio_chunk])
                        raw_text = result[0].text if result and result[0].text else ""
                except torch.cuda.OutOfMemoryError:
                    print("❌ GPU out of memory! Clearing cache...")
                    torch.cuda.empty_cache()
                    consecutive_errors += 1
                    continue
                except Exception as e:
                    print(f"❌ Transcription error: {type(e).__name__}: {str(e)}")
                    consecutive_errors += 1
                    continue
                
                if raw_text.strip():
                    print(f"🎯 Raw transcription: '{raw_text}'")
                    
                    # Process through LocalAgreement with error handling
                    try:
                        state = self.processor.process_transcription(raw_text)
                        
                        # Display current state
                        if state.committed or state.pending:
                            print(f"✅ Committed: '{state.committed}' | ⏳ Pending: '{state.pending}'")
                        
                        # Reset error counter on success
                        consecutive_errors = 0
                        
                    except Exception as e:
                        print(f"❌ LocalAgreement processing error: {type(e).__name__}: {str(e)}")
                        consecutive_errors += 1
                
            except Empty:
                # Queue timeout is normal when no audio is coming in
                continue
            except Exception as e:
                if self.is_recording:  # Only show errors if we're still supposed to be recording
                    print(f"❌ Processing error: {type(e).__name__}: {str(e)}")
                    consecutive_errors += 1
                    
            # Check if we've hit too many consecutive errors
            if consecutive_errors >= max_consecutive_errors:
                print(f"❌ Too many consecutive errors ({consecutive_errors}). Stopping audio processing...")
                self.stop_dictation()
                break
                
        print("🛑 Audio processing thread stopped")
    
    def start_dictation(self):
        """Start dictation (F4 key) with error handling"""
        if self.is_recording:
            print("⚠️  Already recording!")
            return
            
        print("🎙️  Starting dictation...")
        
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
                
                print("✅ Dictation active! Speak now...")
                print("   - Text will appear where your cursor is")
                print("   - Press F4 again to stop")
                
            except Exception as e:
                print(f"❌ Failed to start audio stream: {type(e).__name__}: {str(e)}")
                self.is_recording = False
                raise
                
        except Exception as e:
            print(f"❌ Failed to start dictation: {type(e).__name__}: {str(e)}")
            self.is_recording = False
    
    def stop_dictation(self):
        """Stop dictation (F4 key) with graceful shutdown"""
        if not self.is_recording:
            print("⚠️  Not currently recording!")
            return
            
        print("🛑 Stopping dictation...")
        self.is_recording = False
        
        # Stop audio stream
        if hasattr(self, 'stream') and self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                print(f"⚠️  Error stopping audio stream: {type(e).__name__}: {str(e)}")
            finally:
                self.stream = None
        
        # Wait for processing thread to finish
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5.0)
            if self.processing_thread.is_alive():
                print("⚠️  Processing thread did not stop cleanly")
        
        # Process any remaining pending text with error handling
        try:
            if self.processor.buffer.pending_words:
                pending_text = " ".join(self.processor.buffer.pending_words)
                print(f"📝 Flushing pending text: '{pending_text}'")
                self.output_text(pending_text)  # Use our error-handled output method
        except Exception as e:
            print(f"❌ Error flushing pending text: {type(e).__name__}: {str(e)}")
        
        # Clear the audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except Empty:
                break
        
        print("✅ Dictation stopped")
    
    def toggle_dictation(self):
        """Toggle dictation on/off"""
        if self.is_recording:
            self.stop_dictation()
        else:
            self.start_dictation()
    
    def cleanup(self):
        """Comprehensive cleanup of all resources"""
        print("\n🧹 Performing cleanup...")
        
        # Stop dictation if running
        if self.is_recording:
            self.stop_dictation()
        
        # Clear any remaining GPU memory
        try:
            if hasattr(self, 'model'):
                del self.model
                torch.cuda.empty_cache()
                print("✅ GPU memory cleared")
        except Exception as e:
            print(f"⚠️  Error clearing GPU memory: {e}")
        
        # Close any remaining streams
        if hasattr(self, 'stream') and self.stream:
            try:
                self.stream.abort()
                self.stream.close()
            except:
                pass
        
        print("✅ Cleanup completed")

def main(device_index=None, device_name=None, list_devices=False):
    """Main entry point with comprehensive error handling"""
    
    # Just list devices if requested
    if list_devices:
        AudioDeviceManager.print_input_devices()
        return
    
    print("🚀 Simple Parakeet Dictation System")
    print("=" * 50)
    
    dictation = None
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print("\n\n⚠️  Signal received, shutting down gracefully...")
        if dictation:
            dictation.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create dictation system with error handling
        print("🔧 Initializing system...")
        dictation = SimpleDictation(device_index=device_index, device_name=device_name)
        
        # Set up hotkey (F4 to toggle)
        print("⌨️  Setting up hotkey...")
        keyboard.add_hotkey('f4', dictation.toggle_dictation)
        print("✅ Hotkey registered: F4 to start/stop dictation")
        
        print("\n🎯 READY TO USE:")
        print("   1. Click in any text field (Notepad, browser, etc.)")
        print("   2. Press F4 to start dictation")
        print("   3. Speak clearly")
        print("   4. Watch text appear with LocalAgreement buffering")
        print("   5. Press F4 again to stop")
        print("   6. Press Ctrl+C to quit")
        print("\n⏳ Waiting for F4...")
        
        # Keep running until Ctrl+C
        keyboard.wait('ctrl+c')
        
    except KeyboardInterrupt:
        print("\n\n🔄 Shutting down...")
        
    except sd.PortAudioError as e:
        print(f"\n❌ Audio device error: {e}")
        print("   - Check if microphone is connected")
        print("   - Try closing other applications using the microphone")
        print("   - Check Windows sound settings")
        
    except torch.cuda.CudaError as e:
        print(f"\n❌ CUDA/GPU error: {e}")
        print("   - Check if NVIDIA drivers are installed")
        print("   - Try restarting the application")
        print("   - Check GPU memory usage with nvidia-smi")
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("   - Check if all dependencies are installed")
        print("   - Run: pip install -r requirements.txt")
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        
        # Comprehensive cleanup
        if dictation:
            try:
                dictation.cleanup()
            except Exception as e:
                print(f"⚠️  Cleanup error: {e}")
        
        # Remove hotkey
        try:
            keyboard.remove_hotkey('f4')
        except:
            pass
            
        print("👋 Goodbye!")


def cli():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="PersonalParakeet - Real-time dictation with NVIDIA Parakeet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Use default audio device
  %(prog)s --list-devices     # List available devices
  %(prog)s --device 2         # Use device index 2
  %(prog)s --device-name "Blue Yeti"  # Use device by name
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
    
    args = parser.parse_args()
    
    # Run main with arguments
    main(
        device_index=args.device,
        device_name=args.device_name,
        list_devices=args.list_devices
    )
        print("   - Check that CUDA is available")
        print("   - Ensure microphone permissions are granted")
        sys.exit(1)

if __name__ == "__main__":
    cli()
