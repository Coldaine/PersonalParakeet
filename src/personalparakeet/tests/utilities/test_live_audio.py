#!/usr/bin/env python3
"""
Live microphone test with real-time audio level monitoring
Allows you to speak and see audio levels in real-time
"""

import sys
import threading
import time

import numpy as np
import sounddevice as sd
from audio_meter import AudioMeter


class LiveAudioMonitor:
    def __init__(self, device_id=7, duration=30):
        self.device_id = device_id
        self.duration = duration
        self.sample_rate = 16000
        self.is_running = False
        self.audio_chunks = []
        self.max_level = 0
        self.total_samples = 0
        self.meter = AudioMeter(voice_threshold=0.01)

    def audio_callback(self, indata, frames, time_info, status):
        """Process audio in real-time"""
        if status:
            print(f"\nAudio Status: {status}")

        # Store audio for analysis
        self.audio_chunks.append(indata.copy())
        self.total_samples += len(indata)

        # Measure audio levels
        level = self.meter.measure(indata)
        self.max_level = max(self.max_level, level.peak)

        # Get formatted status line
        status_line = self.meter.get_status_line(level)

        # Print with proper terminal handling
        # Move to start of line and clear it
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.write(status_line)
        sys.stdout.flush()

    def run(self):
        """Run the live audio monitor"""
        print(f"\n🎤 LIVE AUDIO MONITOR - {self.duration} seconds")
        print("=" * 70)
        print(f"Device: HyperX QuadCast (ID: {self.device_id})")
        print(f"Sample Rate: {self.sample_rate} Hz")
        print("\nSpeak into your microphone to see real-time levels!")
        print("Try saying different words and phrases at different volumes.\n")
        print("Legend: 🎤 SPEAKING = Voice detected | SILENCE = No voice")
        print("-" * 70)

        try:
            # Start audio stream
            with sd.InputStream(
                device=self.device_id,
                samplerate=self.sample_rate,
                channels=1,
                callback=self.audio_callback,
                blocksize=512,
            ):
                self.is_running = True
                start_time = time.time()

                # Run for specified duration
                while time.time() - start_time < self.duration:
                    remaining = self.duration - (time.time() - start_time)
                    # Update remaining time without interfering with meter display
                    time.sleep(0.1)

                self.is_running = False

            # Clear the line with ANSI escape code
            sys.stdout.write("\r\033[K")
            sys.stdout.flush()

            # Analysis
            print("\n" + "=" * 70)
            print("📊 AUDIO SESSION ANALYSIS")
            print("=" * 70)

            if self.audio_chunks:
                # Combine all audio
                all_audio = np.concatenate(self.audio_chunks, axis=0)[:, 0]

                # Calculate statistics
                total_rms = np.sqrt(np.mean(all_audio**2))
                avg_db = 20 * np.log10(total_rms + 1e-10)
                max_db = 20 * np.log10(self.max_level + 1e-10)

                # Detect speech segments
                chunk_size = 1600  # 100ms chunks
                speech_chunks = 0
                total_chunks = len(all_audio) // chunk_size

                for i in range(0, len(all_audio) - chunk_size, chunk_size):
                    chunk = all_audio[i : i + chunk_size]
                    chunk_rms = np.sqrt(np.mean(chunk**2))
                    if chunk_rms > 0.01:
                        speech_chunks += 1

                speech_percentage = (speech_chunks / total_chunks) * 100 if total_chunks > 0 else 0

                print(f"Total Duration: {len(all_audio) / self.sample_rate:.1f} seconds")
                print(f"Total Samples: {len(all_audio):,}")
                print(f"Average Level: {avg_db:.1f} dB")
                print(f"Peak Level: {max_db:.1f} dB")
                print(f"Speech Activity: {speech_percentage:.1f}% of time")

                # Quality assessment
                print("\n🎯 AUDIO QUALITY ASSESSMENT:")
                if avg_db > -40 and max_db > -20:
                    print("✅ EXCELLENT - Perfect for speech recognition")
                elif avg_db > -50 and max_db > -30:
                    print("✅ GOOD - Suitable for speech recognition")
                elif avg_db > -60:
                    print("⚠️  FAIR - May need to speak louder or move closer")
                else:
                    print("❌ POOR - Check microphone settings or positioning")

                if speech_percentage > 20:
                    print(f"✅ Good amount of speech detected ({speech_percentage:.0f}%)")
                else:
                    print(
                        f"💡 Try speaking more during the test ({speech_percentage:.0f}% speech detected)"
                    )

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            return False

        return True


def main():
    """Run the live audio test"""
    print("🎙️  PersonalParakeet v3 - Live Audio Test")
    print("=" * 70)

    # Use HyperX QuadCast directly
    device_id = 7
    duration = 20  # 20 seconds by default

    # Check command line arguments
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print(f"Invalid duration: {sys.argv[1]}")
            print("Usage: python test_live_audio.py [duration_in_seconds]")
            return

    print(f"Starting {duration}-second live audio test...")
    print("Press Ctrl+C to stop early\n")

    # Run the monitor
    monitor = LiveAudioMonitor(device_id=device_id, duration=duration)

    try:
        success = monitor.run()
        if success:
            print("\n✅ Test completed successfully!")
            print("\nYour microphone is working well for PersonalParakeet.")
        else:
            print("\n❌ Test failed - check your audio settings")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        print("Partial results may be shown above.")


if __name__ == "__main__":
    main()
