"""Integration test for full pipeline without GUI - real hardware, no mocks."""

import asyncio
import queue
import threading
import time
from datetime import datetime

import numpy as np
import sounddevice as sd

from personalparakeet.config import V3Config
from personalparakeet.core.stt_factory import STTFactory
from personalparakeet.core.text_injector import TextInjector
from personalparakeet.core.vad_engine import VoiceActivityDetector


class PipelineRunner:
    """Runs the full STT pipeline without GUI for testing."""

    def __init__(self, audio_device=None):
        self.config = V3Config()
        # Override audio device if specified
        if audio_device is not None:
            self.config.audio.device_index = audio_device
        self.audio_queue = queue.Queue(maxsize=100)
        self.is_running = False
        self.stt_thread = None

        # Initialize components
        print("🎤 Initializing STT processor...")
        self.stt_processor = STTFactory.create_stt_processor(self.config)

        print("🔊 Initializing VAD processor...")
        self.vad_processor = VoiceActivityDetector(
            sample_rate=self.config.audio.sample_rate,
            silence_threshold=self.config.vad.silence_threshold,
            pause_threshold=self.config.vad.pause_threshold,
        )

        print("⌨️ Initializing text injector...")
        self.text_injector = TextInjector()

        # Audio stream
        self.stream = None

    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream."""
        if status:
            print(f"⚠️ Audio status: {status}")

        if self.is_running:
            try:
                # Convert to float32 and put in queue
                audio_data = indata[:, 0].astype(np.float32)
                self.audio_queue.put(audio_data, block=False)

                # Debug: show audio level
                rms = np.sqrt(np.mean(audio_data**2))
                if rms > 0.001:
                    print(f"🎵 Audio level: {rms:.4f}")
            except queue.Full:
                print("⚠️ Audio queue full, dropping frame")

    def stt_worker(self):
        """Background thread for STT processing."""
        print("🚀 STT worker started")

        while self.is_running:
            try:
                # Get audio chunk
                audio_chunk = self.audio_queue.get(timeout=0.1)

                # Check for speech
                vad_result = self.vad_processor.process_audio_frame(audio_chunk)
                has_speech = vad_result.get("is_speech", False)

                if has_speech:
                    print("🗣️ Speech detected!")
                    # Process with STT
                    text = self.stt_processor.transcribe(audio_chunk)

                    if text and text.strip():
                        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                        print(f"\n[{timestamp}] 🎯 Transcribed: '{text}'")

                        # Inject text
                        try:
                            self.text_injector.inject_text(text)
                            print(f"[{timestamp}] ✅ Text injected successfully")
                        except Exception as e:
                            print(f"[{timestamp}] ❌ Text injection failed: {e}")

            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ STT worker error: {e}")
                import traceback

                traceback.print_exc()

    def start(self):
        """Start the pipeline."""
        print("\n" + "=" * 60)
        print("🎙️ PersonalParakeet Pipeline Test (No GUI)")
        print("=" * 60)
        print("✅ Speak into your microphone - text will be transcribed and injected")
        print("⏹️ Press Ctrl+C to stop")
        print("=" * 60 + "\n")

        self.is_running = True

        # Start audio stream
        self.stream = sd.InputStream(
            device=self.config.audio.device_index,
            channels=1,
            samplerate=self.config.audio.capture_sample_rate,
            blocksize=int(self.config.audio.capture_sample_rate * 0.5),  # 0.5 second chunks
            callback=self.audio_callback,
        )
        self.stream.start()
        # Show device info
        if self.config.audio.device_index is not None:
            device_info = sd.query_devices(self.config.audio.device_index)
            print(
                f"🎤 Audio stream started (device #{self.config.audio.device_index}: {device_info['name']})"
            )
        else:
            device_info = sd.query_devices(sd.default.device[0])
            print(f"🎤 Audio stream started (default device: {device_info['name']})")

        # Start STT worker thread
        self.stt_thread = threading.Thread(target=self.stt_worker, daemon=True)
        self.stt_thread.start()

        print("🔄 Pipeline is running...\n")

    def stop(self):
        """Stop the pipeline."""
        print("\n⏹️ Stopping pipeline...")
        self.is_running = False

        if self.stream:
            self.stream.stop()
            self.stream.close()

        if self.stt_thread:
            self.stt_thread.join(timeout=2.0)

        print("✅ Pipeline stopped")


def test_full_pipeline_no_gui():
    """Test the full pipeline without GUI - manual test with real hardware."""
    runner = PipelineRunner()

    try:
        runner.start()

        # Run for specified duration or until interrupted
        print("🎤 Listening... (speak into your microphone)")
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    finally:
        runner.stop()


if __name__ == "__main__":
    # Run the test
    test_full_pipeline_no_gui()
