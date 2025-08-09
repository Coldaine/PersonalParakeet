#!/usr/bin/env python3
"""
Live Audio Monitor for GUI (Rust+EGUI Dashboard)
Outputs structured data that the dashboard can parse
"""

import sounddevice as sd
import numpy as np
import time
import sys
import json
from audio_meter import AudioMeter


class LiveAudioMonitorGUI:
    def __init__(self, device_id=7, duration=30):
        self.device_id = device_id
        self.duration = duration
        self.sample_rate = 16000
        self.meter = AudioMeter(voice_threshold=0.01)
        
    def audio_callback(self, indata, frames, time_info, status):
        """Process audio and output JSON data"""
        if status:
            print(json.dumps({"type": "error", "message": str(status)}))
            return
        
        # Measure audio levels
        level = self.meter.measure(indata)
        
        # Output structured data
        data = {
            "type": "audio_level",
            "rms": level.rms,
            "peak": level.peak,
            "rms_db": level.rms_db,
            "peak_db": level.peak_db,
            "is_voice": level.is_voice,
            "meter": self.meter.get_ascii_meter(level, width=30),
            "sparkline": self.meter.get_sparkline(samples=15),
            "status": "SPEAKING" if level.is_voice else "SILENCE"
        }
        print(json.dumps(data))
        sys.stdout.flush()
        
    def run(self):
        """Run the monitor with GUI-friendly output"""
        # Send initialization info
        print(json.dumps({
            "type": "init",
            "device_id": self.device_id,
            "sample_rate": self.sample_rate,
            "duration": self.duration
        }))
        
        try:
            with sd.InputStream(
                device=self.device_id,
                samplerate=self.sample_rate,
                channels=1,
                callback=self.audio_callback,
                blocksize=512
            ):
                start_time = time.time()
                
                while time.time() - start_time < self.duration:
                    remaining = self.duration - (time.time() - start_time)
                    print(json.dumps({
                        "type": "progress",
                        "remaining": remaining,
                        "elapsed": time.time() - start_time
                    }))
                    time.sleep(0.5)
                
            # Send completion
            print(json.dumps({
                "type": "complete",
                "message": "Audio monitoring completed"
            }))
            
        except Exception as e:
            print(json.dumps({
                "type": "error",
                "message": str(e)
            }))
            return False
        
        return True


def main():
    """Run the GUI audio monitor"""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=20)
    parser.add_argument("--device", type=int, default=7)
    args = parser.parse_args()
    
    monitor = LiveAudioMonitorGUI(device_id=args.device, duration=args.duration)
    monitor.run()


if __name__ == "__main__":
    main()
