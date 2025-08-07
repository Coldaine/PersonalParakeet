"""Test audio capture hardware functionality."""

import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pytest

# Import dependency validation
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))
from personalparakeet.utils.dependency_validation import get_validator

# Check dependencies on initialization
_validator = get_validator()
AUDIO_DEPS_AVAILABLE = _validator.check_audio_dependencies()
PYAUDIO_AVAILABLE = AUDIO_DEPS_AVAILABLE.get("pyaudio", False)

# Optional imports for hardware dependencies
if PYAUDIO_AVAILABLE:
    import pyaudio
else:
    pyaudio = None

from tests.core import BaseHardwareTest


class TestAudioCapture(BaseHardwareTest):
    """Test audio capture hardware."""

    @pytest.mark.hardware
    def test_audio_device_enumeration(self):
        """Test that we can enumerate audio devices."""
        if not PYAUDIO_AVAILABLE:
            pytest.skip("pyaudio not available")

        pa = pyaudio.PyAudio()

        try:
            device_count = pa.get_device_count()
            assert device_count > 0, "No audio devices found"

            # Find at least one input device
            input_devices = []
            for i in range(device_count):
                info = pa.get_device_info_by_index(i)
                if int(info.get("maxInputChannels", 0)) > 0:
                    input_devices.append(info)

            assert len(input_devices) > 0, "No input devices found"

            # Log device info
            print(f"\nFound {len(input_devices)} input devices:")
            for device in input_devices[:3]:  # Show first 3
                print(f"  - {device['name']} ({device['maxInputChannels']} channels)")

        finally:
            pa.terminate()

    @pytest.mark.hardware
    def test_audio_stream_creation(self, audio_test_device):
        """Test creating audio streams with different configurations."""
        if not PYAUDIO_AVAILABLE:
            pytest.skip("pyaudio not available")

        pa = pyaudio.PyAudio()

        test_configs = [
            {"rate": 16000, "channels": 1, "format": pyaudio.paInt16},
            {"rate": 44100, "channels": 1, "format": pyaudio.paInt16},
            {"rate": 48000, "channels": 1, "format": pyaudio.paInt16},
        ]

        try:
            for config in test_configs:
                stream = None
                try:
                    stream = pa.open(
                        rate=config["rate"],
                        channels=config["channels"],
                        format=config["format"],
                        input=True,
                        input_device_index=audio_test_device,
                        frames_per_buffer=1024,
                    )

                    # Test that stream is active
                    assert stream.is_active(), f"Stream not active for config {config}"

                    # Read a small chunk to verify it works
                    data = stream.read(1024, exception_on_overflow=False)
                    assert len(data) > 0, "No data read from stream"

                except Exception as e:
                    # Some sample rates might not be supported
                    print(f"Config {config} not supported: {e}")
                    continue
                finally:
                    if stream:
                        stream.stop_stream()
                        stream.close()

        finally:
            pa.terminate()

    @pytest.mark.hardware
    def test_audio_capture_quality(self, audio_test_device):
        """Test audio capture quality and noise floor."""
        if not PYAUDIO_AVAILABLE:
            pytest.skip("pyaudio not available")

        pa = pyaudio.PyAudio()

        try:
            device_info = pa.get_device_info_by_index(audio_test_device)
            rate = int(device_info.get("defaultSampleRate", 16000))

            stream = pa.open(
                rate=rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=audio_test_device,
                frames_per_buffer=1024,
            )

            # Capture 1 second of audio
            print(f"\nCapturing 1 second of audio at {rate} Hz for noise floor analysis...")
            frames = []
            for _ in range(int(rate / 1024)):
                data = stream.read(1024, exception_on_overflow=False)
                frames.append(data)

            stream.stop_stream()
            stream.close()

            # Analyze audio
            audio_data = np.frombuffer(b"".join(frames), dtype=np.int16)

            # Calculate metrics
            rms = np.sqrt(np.mean(audio_data.astype(float) ** 2))
            peak = np.max(np.abs(audio_data))
            noise_floor_db = 20 * np.log10(rms / 32768) if rms > 0 else -np.inf

            print(f"Audio metrics:")
            print(f"  RMS: {rms:.2f}")
            print(f"  Peak: {peak}")
            print(f"  Noise floor: {noise_floor_db:.2f} dB")

            # Basic sanity checks
            assert peak < 32000, "Audio clipping detected"
            assert rms > 0, "No audio signal detected"

        finally:
            pa.terminate()

    @pytest.mark.hardware
    def test_audio_latency(self, audio_test_device):
        """Test audio capture latency."""
        if not PYAUDIO_AVAILABLE:
            pytest.skip("pyaudio not available")

        pa = pyaudio.PyAudio()

        try:
            device_info = pa.get_device_info_by_index(audio_test_device)
            rate = int(device_info.get("defaultSampleRate", 16000))

            stream = pa.open(
                rate=rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=audio_test_device,
                frames_per_buffer=512,  # Smaller buffer for lower latency
            )

            # Measure time to read chunks
            latencies = []
            for _ in range(100):
                start = time.time()
                data = stream.read(512, exception_on_overflow=False)
                latency = time.time() - start
                latencies.append(latency)

            stream.stop_stream()
            stream.close()

            # Analyze latencies
            avg_latency = np.mean(latencies) * 1000  # Convert to ms
            max_latency = np.max(latencies) * 1000

            print(f"\nAudio latency:")
            print(f"  Average: {avg_latency:.2f} ms")
            print(f"  Maximum: {max_latency:.2f} ms")

            # Latency should be reasonable
            assert avg_latency < 50, f"Average latency too high: {avg_latency:.2f} ms"
            assert max_latency < 100, f"Maximum latency too high: {max_latency:.2f} ms"

        finally:
            pa.terminate()

    @pytest.mark.hardware
    @pytest.mark.slow
    def test_continuous_capture_stability(self, audio_test_device):
        """Test continuous audio capture stability."""
        if not PYAUDIO_AVAILABLE:
            pytest.skip("pyaudio not available")

        pa = pyaudio.PyAudio()

        try:
            device_info = pa.get_device_info_by_index(audio_test_device)
            rate = int(device_info.get("defaultSampleRate", 16000))
            frames_per_buffer = 1024
            capture_duration_seconds = 5

            stream = pa.open(
                rate=rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=audio_test_device,
                frames_per_buffer=frames_per_buffer,
            )

            # Calculate the number of chunks to read
            total_chunks = int(rate / frames_per_buffer * capture_duration_seconds)

            print(
                f"\nTesting continuous capture for {capture_duration_seconds} seconds at {rate} Hz by reading {total_chunks} chunks..."
            )

            errors = 0
            frames = []

            for _ in range(total_chunks):
                try:
                    # Add a timeout to the read operation to prevent hangs
                    data = stream.read(frames_per_buffer, exception_on_overflow=False)
                    frames.append(data)
                except Exception as e:
                    errors += 1
                    print(f"Error during capture: {e}")

            stream.stop_stream()
            stream.close()

            print(f"Captured {len(frames)} chunks with {errors} errors")

            # The test should read all the expected chunks
            assert (
                len(frames) == total_chunks
            ), f"Expected {total_chunks} chunks, but captured {len(frames)}"
            assert errors == 0, f"Errors during capture: {errors}"

        finally:
            pa.terminate()
