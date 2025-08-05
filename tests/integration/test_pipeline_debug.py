"""Debug version of pipeline test with more output."""

import time
from test_pipeline_no_gui import PipelineRunner

def test_pipeline_debug(duration=5, audio_device=7):
    """Test with debug output."""
    print("\n" + "="*60)
    print(f"🎤 {duration}-SECOND DEBUG PIPELINE TEST")
    print("="*60)
    print("✅ Speak into your microphone NOW!")
    print("✅ Audio levels will be shown")
    print(f"⏱️ Test will run for {duration} seconds...")
    print("="*60 + "\n")
    
    runner = PipelineRunner(audio_device=audio_device)
    
    try:
        runner.start()
        
        # Run for specified duration
        start_time = time.time()
        while time.time() - start_time < duration:
            time.sleep(0.1)
            
        print(f"\n⏱️ {duration} seconds elapsed")
        
    finally:
        runner.stop()
    
    print("\n✅ Test completed")


if __name__ == "__main__":
    import sys
    
    # Default values
    duration = 5
    device = 7
    
    # Parse arguments
    if len(sys.argv) > 1:
        duration = int(sys.argv[1])
    if len(sys.argv) > 2:
        device = int(sys.argv[2])
    
    test_pipeline_debug(duration=duration, audio_device=device)