#!/usr/bin/env python3
"""
Headless audio test - captures audio without real-time display
Perfect for automated testing or when you don't need live feedback
"""

import sys
import time

import numpy as np
import sounddevice as sd


class HeadlessAudioTest:
    def __init__(self, device_id=7, duration=20):
        self.device_id = device_id
        self.duration = duration
        self.sample_rate = 16000
        self.audio_chunks = []
        self.max_level = 0
        self.total_samples = 0
        self.speech_frames = 0
        self.total_frames = 0

    def audio_callback(self, indata, frames, time_info, status):
        """Process audio silently"""
        if status:
            # Store status errors but don't print
            pass

        # Store audio for analysis
        self.audio_chunks.append(indata.copy())
        self.total_samples += len(indata)
        self.total_frames += 1

        # Calculate levels
        audio = indata[:, 0]
        rms = np.sqrt(np.mean(audio**2))
        peak = np.max(np.abs(audio))
        self.max_level = max(self.max_level, peak)

        # Track speech activity
        if rms > 0.01:
            self.speech_frames += 1

    def run(self):
        """Run the headless audio test"""
        print(f"🎤 Starting {self.duration}-second audio test (headless mode)...")
        print(f"Device: HyperX QuadCast (ID: {self.device_id})")
        print(f"Speak naturally during the test.\n")

        try:
            # Start audio stream
            with sd.InputStream(
                device=self.device_id,
                samplerate=self.sample_rate,
                channels=1,
                callback=self.audio_callback,
                blocksize=512,
            ):
                # Simple progress indicator
                start_time = time.time()
                dots = 0
                while time.time() - start_time < self.duration:
                    remaining = self.duration - (time.time() - start_time)
                    # Update every 2 seconds
                    if int(remaining) % 2 == 0 and dots < int(self.duration / 2):
                        print(".", end="", flush=True)
                        dots += 1
                    time.sleep(0.5)

                print("\n")

            # Analysis
            if self.audio_chunks:
                # Combine all audio
                all_audio = np.concatenate(self.audio_chunks, axis=0)[:, 0]

                # Calculate statistics
                total_rms = np.sqrt(np.mean(all_audio**2))
                avg_db = 20 * np.log10(total_rms + 1e-10)
                max_db = 20 * np.log10(self.max_level + 1e-10)

                # Speech percentage
                speech_percentage = (
                    (self.speech_frames / self.total_frames) * 100 if self.total_frames > 0 else 0
                )

                # Generate report
                print("=" * 50)
                print("📊 AUDIO TEST RESULTS")
                print("=" * 50)
                print(f"Duration: {len(all_audio) / self.sample_rate:.1f} seconds")
                print(f"Average Level: {avg_db:.1f} dB")
                print(f"Peak Level: {max_db:.1f} dB")
                print(f"Speech Activity: {speech_percentage:.1f}% of time")

                # Quality assessment
                print("\n🎯 ASSESSMENT:")
                quality_score = 0

                if avg_db > -40 and max_db > -20:
                    print("✅ Audio levels: EXCELLENT")
                    quality_score += 3
                elif avg_db > -50 and max_db > -30:
                    print("✅ Audio levels: GOOD")
                    quality_score += 2
                else:
                    print("⚠️  Audio levels: LOW (speak louder/closer)")
                    quality_score += 1

                if speech_percentage > 30:
                    print(f"✅ Speech detected: {speech_percentage:.0f}% (good coverage)")
                    quality_score += 2
                elif speech_percentage > 10:
                    print(f"⚠️  Speech detected: {speech_percentage:.0f}% (speak more)")
                    quality_score += 1
                else:
                    print(f"❌ Speech detected: {speech_percentage:.0f}% (too quiet)")

                # Overall verdict
                print(f"\n📋 OVERALL: ", end="")
                if quality_score >= 4:
                    print("Ready for PersonalParakeet! ✅")
                    return True, "excellent"
                elif quality_score >= 3:
                    print("Acceptable, but could be better 👍")
                    return True, "good"
                else:
                    print("Needs adjustment ⚠️")
                    return False, "poor"

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            return False, "error"

        return True, "unknown"


def main():
    """Run the headless audio test"""
    # Parse arguments
    duration = 20
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
            duration = max(5, min(60, duration))  # Clamp between 5-60 seconds
        except ValueError:
            pass

    # Run test
    test = HeadlessAudioTest(device_id=7, duration=duration)
    success, quality = test.run()

    # Exit code based on success
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
