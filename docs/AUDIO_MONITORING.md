# Audio Monitoring Guide

PersonalParakeet provides real-time audio monitoring tools for testing and debugging your microphone setup.

## Quick Start

### Terminal Audio Monitor
```bash
# Run from project root
poetry run python src/personalparakeet/tests/utilities/test_live_audio.py

# Specify duration (default 20 seconds)
poetry run python src/personalparakeet/tests/utilities/test_live_audio.py 30
```

### GUI Dashboard
```bash
# Note: GUI dashboard has been removed in favor of Rust UI
# Use terminal monitor instead
```

## Audio Level Display

The audio monitor shows real-time levels in multiple formats:

### Visual Meter
```
🎤 SPEAKING [████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░] RMS: -36.5 dB | Peak: -19.2 dB
   SILENCE  [██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] RMS: -50.1 dB | Peak: -41.9 dB
```

- **Status**: Shows "🎤 SPEAKING" when voice is detected, "SILENCE" otherwise
- **Meter**: Visual bar showing audio level (filled = louder)
- **RMS**: Root Mean Square level in decibels (average loudness)
- **Peak**: Maximum amplitude in decibels (loudest point)

### Understanding dB Levels

| Level Range | Quality | Description |
|-------------|---------|-------------|
| > -20 dB | Excellent | Very loud, may clip |
| -30 to -20 dB | Good | Normal speaking voice |
| -40 to -30 dB | Fair | Soft speaking, still usable |
| -50 to -40 dB | Poor | Very quiet, may miss words |
| < -50 dB | Silent | Background noise only |

## Voice Activity Detection

The monitor detects when you're speaking vs silence:
- **Threshold**: RMS > 0.01 (adjustable)
- **Visual**: Different meter styles for voice vs silence
- **Analysis**: Shows percentage of time speaking

## Audio Quality Assessment

After monitoring, you'll see an analysis:
```
📊 AUDIO SESSION ANALYSIS
======================================================================
Total Duration: 20.1 seconds
Total Samples: 321,600
Average Level: -42.3 dB
Peak Level: -19.2 dB
Speech Activity: 35.2% of time

🎯 AUDIO QUALITY ASSESSMENT:
✅ GOOD - Suitable for speech recognition
✅ Good amount of speech detected (35%)
```

## Troubleshooting

### No Audio Input
- Check microphone permissions
- Verify device ID (default: 7 for HyperX QuadCast)
- Try listing devices: `python -m sounddevice`

### Terminal Display Issues
The meter uses ANSI escape codes for proper display:
- `\r` - Carriage return (back to line start)
- `\033[K` - Clear from cursor to end of line

If you see garbled output, your terminal may not support ANSI codes.

### Terminal Display Issues
If the meter doesn't update properly in your terminal:
1. Ensure your terminal supports ANSI escape codes
2. Try the GUI-specific monitor: `test_live_audio_gui.py`

## Technical Details

### Audio Meter Module
The `audio_meter.py` module provides:
- **AudioLevel**: Data class for measurements
- **AudioMeter**: Main meter class with multiple formats
  - Bar meters (Unicode/ASCII)
  - Percentage meters
  - Level indicators
  - Sparkline graphs

### Callback Processing
Audio is processed in real-time via callback:
```python
def audio_callback(self, indata, frames, time_info, status):
    # Process 512 samples at 16kHz = 32ms chunks
    level = self.meter.measure(indata)
    # Update display
```

### Performance
- Sample rate: 16kHz (optimal for speech)
- Block size: 512 samples (32ms latency)
- Update rate: ~30 Hz (smooth visual updates)

## Integration with PersonalParakeet

The audio monitoring uses the same components as the main app:
- **Device Selection**: Same device ID as main config
- **VAD Threshold**: Matches voice detection settings
- **Audio Pipeline**: Tests the same processing chain

This ensures your tests accurately reflect real usage.
