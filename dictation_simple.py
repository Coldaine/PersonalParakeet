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

# Import your LocalAgreement logic
from ESSENTIAL_LocalAgreement_Code import TranscriptionProcessor

class SimpleDictation:
    def __init__(self):
        print("🔧 Initializing Simple Parakeet Dictation...")
        
        # Audio settings (optimized for real-time dictation)
        self.sample_rate = 16000
        self.chunk_duration = 1.0  # 1 second chunks for more responsive processing
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        
        # State
        self.is_recording = False
        self.audio_queue = Queue()
        
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
        
    def output_text(self, text):
        """Output committed text via keyboard"""
        print(f"📝 OUTPUT CALLBACK TRIGGERED: '{text}'")
        try:
            keyboard.write(text + " ")  # Add space after each word/phrase
            print(f"✅ Successfully wrote text: '{text}'")
        except Exception as e:
            print(f"❌ Failed to write text: {e}")
        
    def audio_callback(self, indata, frames, time, status):
        """Audio input callback - queues chunks for processing"""
        if status:
            print(f"⚠️  Audio status: {status}")
            
        if self.is_recording:
            # Convert to float32 and add to queue
            audio_chunk = indata[:, 0].astype(np.float32)
            self.audio_queue.put(audio_chunk.copy())
    
    def process_audio_loop(self):
        """Background thread that processes audio chunks"""
        print("🎤 Audio processing thread started")
        
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
                with torch.inference_mode():
                    result = self.model.transcribe([audio_chunk])
                    raw_text = result[0].text if result and result[0].text else ""
                
                if raw_text.strip():
                    print(f"🎯 Raw transcription: '{raw_text}'")
                    
                    # Process through LocalAgreement
                    state = self.processor.process_transcription(raw_text)
                    
                    # Display current state
                    if state.committed or state.pending:
                        print(f"✅ Committed: '{state.committed}' | ⏳ Pending: '{state.pending}'")
                
            except Empty:
                # Queue timeout is normal when no audio is coming in
                continue
            except Exception as e:
                if self.is_recording:  # Only show errors if we're still supposed to be recording
                    print(f"❌ Processing error: {type(e).__name__}: {str(e)}")
                
        print("🛑 Audio processing thread stopped")
    
    def start_dictation(self):
        """Start dictation (F4 key)"""
        if self.is_recording:
            print("⚠️  Already recording!")
            return
            
        print("🎙️  Starting dictation...")
        self.is_recording = True
        
        # Start audio processing thread
        self.processing_thread = threading.Thread(target=self.process_audio_loop)
        self.processing_thread.start()
        
        # Start audio stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self.audio_callback,
            blocksize=self.chunk_size
        )
        self.stream.start()
        
        print("✅ Dictation active! Speak now...")
        print("   - Text will appear where your cursor is")
        print("   - Press F4 again to stop")
    
    def stop_dictation(self):
        """Stop dictation (F4 key)"""
        if not self.is_recording:
            print("⚠️  Not currently recording!")
            return
            
        print("🛑 Stopping dictation...")
        self.is_recording = False
        
        # Stop audio stream
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        # Wait for processing thread to finish
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)
        
        # Process any remaining pending text
        if self.processor.buffer.pending_words:
            pending_text = " ".join(self.processor.buffer.pending_words)
            print(f"📝 Flushing pending text: '{pending_text}'")
            keyboard.write(pending_text + " ")
        
        print("✅ Dictation stopped")
    
    def toggle_dictation(self):
        """Toggle dictation on/off"""
        if self.is_recording:
            self.stop_dictation()
        else:
            self.start_dictation()

def main():
    print("🚀 Simple Parakeet Dictation System")
    print("=" * 50)
    
    try:
        # Create dictation system
        dictation = SimpleDictation()
        
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
        if 'dictation' in locals():
            dictation.stop_dictation()
        print("👋 Goodbye!")
        
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        print("   - Check that CUDA is available")
        print("   - Ensure microphone permissions are granted")
        sys.exit(1)

if __name__ == "__main__":
    main()
