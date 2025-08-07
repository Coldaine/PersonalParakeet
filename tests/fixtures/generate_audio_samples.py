"""Generate sample audio files for testing."""

import numpy as np
import scipy.io.wavfile as wavfile


def generate_sine_wave(frequency, duration, sample_rate=16000):
    """Generate a sine wave."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    return np.sin(2 * np.pi * frequency * t)


def generate_speech_like_audio(duration, sample_rate=16000):
    """Generate audio that resembles speech patterns."""
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Base frequency (fundamental)
    base = 150 + 50 * np.sin(2 * np.pi * 0.5 * t)  # Varying pitch

    # Add harmonics
    audio = np.sin(2 * np.pi * base * t)
    audio += 0.5 * np.sin(2 * np.pi * base * 2 * t)
    audio += 0.3 * np.sin(2 * np.pi * base * 3 * t)

    # Add envelope (speech-like amplitude modulation)
    envelope = np.concatenate(
        [
            np.linspace(0, 1, int(0.1 * sample_rate)),  # Attack
            np.ones(int((duration - 0.2) * sample_rate)),  # Sustain
            np.linspace(1, 0, int(0.1 * sample_rate)),  # Release
        ]
    )

    if len(envelope) > len(audio):
        envelope = envelope[: len(audio)]
    elif len(envelope) < len(audio):
        envelope = np.pad(envelope, (0, len(audio) - len(envelope)))

    audio = audio * envelope

    # Add some noise
    audio += 0.05 * np.random.randn(len(audio))

    return audio


def save_wav(filename, audio, sample_rate=16000):
    """Save audio as WAV file."""
    # Normalize to 16-bit range
    audio = np.clip(audio, -1, 1)
    audio = (audio * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, audio)


def main():
    """Generate all sample audio files."""
    print("Generating sample audio files...")

    # 1. Hello world - short burst
    hello_audio = generate_speech_like_audio(1.5)
    save_wav("audio/hello_world.wav", hello_audio)
    print("✓ Generated hello_world.wav (1.5s)")

    # 2. Commands - medium length with pauses
    commands_audio = []
    for i in range(3):
        # Command
        commands_audio.extend(generate_speech_like_audio(1.0))
        # Pause
        commands_audio.extend(np.zeros(int(16000 * 0.5)))

    commands_audio = np.array(commands_audio[:-8000])  # Remove last pause
    save_wav("audio/commands.wav", commands_audio / np.max(np.abs(commands_audio)))
    print("✓ Generated commands.wav (4.5s)")

    # 3. Continuous speech - longer audio
    continuous_audio = generate_speech_like_audio(10.0)
    save_wav("audio/continuous_speech.wav", continuous_audio)
    print("✓ Generated continuous_speech.wav (10s)")

    # 4. Silence - for noise floor testing
    silence = np.random.randn(16000 * 2) * 0.001  # Very quiet noise
    save_wav("audio/silence.wav", silence)
    print("✓ Generated silence.wav (2s)")

    # 5. Test tone - pure sine wave
    test_tone = generate_sine_wave(440, 1.0)  # A440
    save_wav("audio/test_tone.wav", test_tone * 0.5)
    print("✓ Generated test_tone.wav (1s)")

    print("\nAll sample audio files generated successfully!")


if __name__ == "__main__":
    import os

    os.makedirs("audio", exist_ok=True)
    main()
