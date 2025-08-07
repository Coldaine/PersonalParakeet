"""List available audio devices to find the correct one."""

import sounddevice as sd

print("Available Audio Devices:")
print("=" * 60)

devices = sd.query_devices()
for i, device in enumerate(devices):
    if device["max_input_channels"] > 0:  # Input devices only
        print(f"\nDevice #{i}: {device['name']}")
        print(f"  Channels: {device['max_input_channels']}")
        print(f"  Sample Rate: {device['default_samplerate']} Hz")
        print(f"  Host API: {sd.query_hostapis(device['hostapi'])['name']}")

print("\n" + "=" * 60)
print(f"Current default input device: {sd.default.device[0]}")
print("=" * 60)
