"""Manual integration test for full pipeline - real hardware, no mocks."""

import signal
import sys
import threading
import time

from test_pipeline_no_gui import PipelineRunner


def test_pipeline_manual_10_seconds(audio_device=None):
    """Test the pipeline for 10 seconds - speak into mic during this time."""
    print("\n" + "=" * 60)
    print("🎤 10-SECOND PIPELINE TEST")
    print("=" * 60)
    print("✅ Speak into your microphone NOW!")
    print("✅ Text will be transcribed and injected")
    print("⏱️ Test will run for 10 seconds...")
    print("=" * 60 + "\n")

    runner = PipelineRunner(audio_device=audio_device)

    try:
        runner.start()

        # Run for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            time.sleep(0.1)

        print("\n⏱️ 10 seconds elapsed")

    finally:
        runner.stop()

    print("\n✅ Test completed successfully")


def test_pipeline_continuous():
    """Continuous pipeline test - runs until interrupted."""
    print("\n" + "=" * 60)
    print("🎤 CONTINUOUS PIPELINE TEST")
    print("=" * 60)
    print("✅ Speak into your microphone")
    print("✅ Text will be transcribed and injected")
    print("⏹️ Press Ctrl+C to stop")
    print("=" * 60 + "\n")

    runner = PipelineRunner()

    # Set up signal handler for clean shutdown
    def signal_handler(sig, frame):
        print("\n⚠️ Interrupt received")
        runner.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        runner.start()

        # Run indefinitely
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        pass
    finally:
        runner.stop()


if __name__ == "__main__":
    import sys

    # Check for device argument
    device = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "default":
            device = None  # Use system default
        else:
            device = int(sys.argv[1])

    # Run the 10-second test
    test_pipeline_manual_10_seconds(audio_device=device)
