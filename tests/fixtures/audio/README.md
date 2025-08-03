# Test Audio Fixtures

This directory contains audio files used for testing PersonalParakeet.

## Files

- `hello_world.wav` - Short speech-like audio (1.5s)
- `commands.wav` - Multiple command-like utterances with pauses (4.5s)
- `continuous_speech.wav` - Continuous speech-like audio (10s)
- `silence.wav` - Near-silence for noise floor testing (2s)
- `test_tone.wav` - 440Hz sine wave for calibration (1s)

## Generating Audio Files

To regenerate the audio files, run:

```bash
cd tests/fixtures
python generate_audio_samples.py
```

## Audio Specifications

All audio files use:
- Sample rate: 16000 Hz
- Channels: 1 (mono)
- Bit depth: 16-bit
- Format: WAV

## Note

These are synthetic audio files that simulate speech patterns but don't contain actual speech. They're designed to test audio pipeline functionality without requiring real speech data.