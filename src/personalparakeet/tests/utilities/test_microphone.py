#!/usr/bin/env python3
"""
Test microphone input for PersonalParakeet v3
Checks audio device availability and captures sample audio
"""

import sys
from pathlib import Path

# Import dependency validation
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
from personalparakeet.utils.dependency_validation import get_validator

# Check dependencies on initialization
_validator = get_validator()
AUDIO_DEPS_AVAILABLE = _validator.check_audio_dependencies()
SOUNDDDEVICE_AVAILABLE = AUDIO_DEPS_AVAILABLE.get("sounddevice", False)

# Optional imports for hardware dependencies
if SOUNDDDEVICE_AVAILABLE:
    import sounddevice as sd
else:
    sd = None

import numpy as np
import time


def list_audio_devices():
    """List all available audio devices"""
    if not SOUNDDDEVICE_AVAILABLE:
        print("✗ ERROR: sounddevice not available!")
        print("  Install with: pip install sounddevice")
        return []

    print("=== Available Audio Devices ===")
    print("\nInput Devices:")
    print("-" * 50)

    devices = sd.query_devices()
    input_devices = []

    for i, device in enumerate(devices):
        if int(device["max_input_channels"]) > 0:
            input_devices.append(i)
            print(f"[{i}] {device['name']}")
            print(f"    Channels: {device['max_input_channels']}")
            print(f"    Sample Rate: {device['default_samplerate']} Hz")
            print()

    return input_devices


def test_microphone_input(device_id=None, duration=3):
    """Test microphone input by recording and analyzing audio"""
    if not SOUNDDDEVICE_AVAILABLE:
        print("✗ ERROR: sounddevice not available!")
        print("  Install with: pip install sounddevice")
        return False

    print(f"\n=== Testing Microphone Input ===")

    # Audio parameters
    sample_rate = 16000  # 16kHz for speech
    channels = 1

    if device_id is not None:
        print(f"Using device: {device_id}")
    else:
        print(f"Using default input device")

    print(f"Sample rate: {sample_rate} Hz")
    print(f"Duration: {duration} seconds")
    print(f"Channels: {channels}")

    # Storage for audio data
    audio_data = []

    def audio_callback(indata, frames, time, status):
        """Callback for audio stream"""
        if status:
            print(f"Status: {status}")
        audio_data.append(indata.copy())

    try:
        print("\nStarting recording... Speak into your microphone!")

        # Create and start stream
        with sd.InputStream(
            device=device_id,
            samplerate=sample_rate,
            channels=channels,
            callback=audio_callback,
            blocksize=1024,
        ):
            # Visual countdown
            for i in range(duration):
                print(f"Recording... {duration - i} seconds remaining", end="\r")
                time.sleep(1)
            print("\nRecording complete!")

        # Analyze captured audio
        if audio_data:
            # Concatenate all audio chunks
            audio = np.concatenate(audio_data, axis=0)

            print(f"\n=== Audio Analysis ===")
            print(f"Total samples captured: {len(audio)}")
            print(f"Duration: {len(audio) / sample_rate:.2f} seconds")
            print(f"Audio shape: {audio.shape}")

            # Calculate audio statistics
            audio_flat = audio.flatten()
            rms = np.sqrt(np.mean(audio_flat**2))
            peak = np.max(np.abs(audio_flat))

            print(f"\nAudio Statistics:")
            print(f"RMS Level: {rms:.6f} ({20 * np.log10(rms + 1e-10):.1f} dB)")
            print(f"Peak Level: {peak:.6f} ({20 * np.log10(peak + 1e-10):.1f} dB)")

            # Check if we got meaningful audio
            if rms > 0.001:
                print("\n✓ SUCCESS: Audio signal detected!")
                print("  The microphone is working properly.")
            else:
                print("\n⚠ WARNING: Very low audio level detected.")
                print("  Check if your microphone is muted or too far away.")

            return True
        else:
            print("\n✗ ERROR: No audio data captured!")
            return False

    except Exception as e:
        print(f"\n✗ ERROR: Failed to capture audio: {e}")
        return False


def test_audio_stream_stability(device_id=None, duration=5):
    """Test audio stream stability over time"""
    if not SOUNDDDEVICE_AVAILABLE:
        print("✗ ERROR: sounddevice not available!")
        print("  Install with: pip install sounddevice")
        return False

    print(f"\n=== Testing Audio Stream Stability ===")
    print(f"Testing for {duration} seconds...")

    sample_rate = 16000
    block_count = 0
    error_count = 0

    def callback(indata, frames, time, status):
        nonlocal block_count, error_count
        block_count += 1
        if status:
            error_count += 1
            print(f"\n⚠ Stream error: {status}")

    try:
        with sd.InputStream(
            device=device_id, samplerate=sample_rate, channels=1, callback=callback, blocksize=512
        ):
            start_time = time.time()
            while time.time() - start_time < duration:
                elapsed = time.time() - start_time
                print(
                    f"Streaming... {elapsed:.1f}s - Blocks: {block_count}, Errors: {error_count}",
                    end="\r",
                )
                time.sleep(0.1)

        print(f"\n\nStream Statistics:")
        print(f"Total blocks processed: {block_count}")
        print(f"Errors encountered: {error_count}")
        print(f"Block rate: {block_count / duration:.1f} blocks/second")

        if error_count == 0:
            print("\n✓ Stream is stable - no errors detected!")
        else:
            print(f"\n⚠ Stream had {error_count} errors - may need different settings")

        return error_count == 0

    except Exception as e:
        print(f"\n✗ ERROR: Stream test failed: {e}")
        return False


def test_vad_levels(device_id=None, duration=10):
    """Test Voice Activity Detection levels"""
    if not SOUNDDDEVICE_AVAILABLE:
        print("✗ ERROR: sounddevice not available!")
        print("  Install with: pip install sounddevice")
        return False

    print(f"\n=== Testing Voice Activity Detection Levels ===")
    print(f"Monitoring audio levels for {duration} seconds...")
    print("Try speaking and being silent to see level changes\n")

    sample_rate = 16000

    def callback(indata, frames, time, status):
        # Calculate RMS level
        rms = np.sqrt(np.mean(indata**2))
        db = 20 * np.log10(rms + 1e-10)

        # Create visual meter
        meter_width = 50
        normalized = min(1.0, rms * 20)  # Normalize to 0-1 range
        filled = int(normalized * meter_width)
        meter = "█" * filled + "░" * (meter_width - filled)

        # Determine if voice is likely present
        voice_detected = "VOICE" if rms > 0.01 else "SILENCE"

        print(f"Level: [{meter}] {db:6.1f} dB - {voice_detected}", end="\r")

    try:
        with sd.InputStream(
            device=device_id, samplerate=sample_rate, channels=1, callback=callback, blocksize=512
        ):
            time.sleep(duration)

        print("\n\n✓ VAD level test complete!")
        return True

    except Exception as e:
        print(f"\n✗ ERROR: VAD test failed: {e}")
        return False


def main():
    """Run all microphone tests"""
    print("PersonalParakeet v3 - Microphone Test Suite")
    print("=" * 60)

    # Check if sounddevice is available
    if not SOUNDDDEVICE_AVAILABLE:
        print("✗ ERROR: sounddevice not installed!")
        print("  Install with: pip install sounddevice")
        return

    # List devices
    input_devices = list_audio_devices()

    if not input_devices:
        print("\n✗ ERROR: No input devices found!")
        return

    # Let user select device or use default
    device_id = None
    if len(input_devices) > 1:
        print("\nMultiple input devices available.")
        print("Press Enter to use default, or enter device number: ", end="")
        choice = input().strip()
        if choice and choice.isdigit():
            device_id = int(choice)

    # Run tests
    tests = [
        ("Basic Recording", lambda: test_microphone_input(device_id, 3)),
        ("Stream Stability", lambda: test_audio_stream_stability(device_id, 5)),
        ("VAD Levels", lambda: test_vad_levels(device_id, 10)),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print("=" * 60)

        try:
            success = test_func()
            results.append((test_name, success))
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            break
        except Exception as e:
            print(f"\n✗ Test failed with error: {e}")
            results.append((test_name, False))

        if test_func != tests[-1][1]:
            print("\nPress Enter to continue to next test...")
            input()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{test_name:.<40} {status}")

    # Overall result
    all_passed = all(success for _, success in results)
    print("\nOverall: " + ("✓ All tests passed!" if all_passed else "✗ Some tests failed"))

    if all_passed:
        print("\nYour microphone is working correctly and ready for PersonalParakeet!")
    else:
        print("\nPlease check your microphone settings and permissions.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
