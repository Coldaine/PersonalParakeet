#!/usr/bin/env python3
"""Test Parakeet STT with real speech audio"""

import asyncio
import numpy as np
import scipy.io.wavfile as wavfile
import logging
from pathlib import Path
import os

# Try to import TTS for generating test speech
try:
    from gtts import gTTS
    HAS_TTS = True
except ImportError:
    HAS_TTS = False
    print("gTTS not available, will use synthetic audio")

from personalparakeet.config import V3Config
from personalparakeet.core.stt_factory import STTFactory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_test_speech(text: str, filename: str, sample_rate: int = 16000):
    """Generate test speech audio file"""
    if HAS_TTS:
        # Use Google TTS
        tts = gTTS(text=text, lang='en', slow=False)
        temp_file = filename.replace('.wav', '_temp.mp3')
        tts.save(temp_file)
        
        # Convert to WAV at correct sample rate
        import subprocess
        subprocess.run([
            'ffmpeg', '-i', temp_file, '-ar', str(sample_rate), 
            '-ac', '1', '-y', filename
        ], capture_output=True)
        os.remove(temp_file)
        logger.info(f"Generated speech file: {filename}")
    else:
        # Generate synthetic speech-like audio
        duration = len(text.split()) * 0.5  # Rough estimate
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Create modulated tones that resemble speech patterns
        speech = np.zeros_like(t)
        for i, word in enumerate(text.split()):
            start = int(i * 0.5 * sample_rate)
            end = min(start + int(0.3 * sample_rate), len(t))
            if end > start:
                word_t = t[start:end]
                # Vary frequency based on word
                freq = 200 + (ord(word[0]) - 65) * 10
                speech[start:end] = np.sin(2 * np.pi * freq * word_t) * 0.3
                # Add harmonics
                speech[start:end] += np.sin(4 * np.pi * freq * word_t) * 0.1
                speech[start:end] += np.sin(6 * np.pi * freq * word_t) * 0.05
        
        # Add envelope
        envelope = np.exp(-t * 0.5)
        speech = speech * envelope
        
        # Add some noise
        speech += np.random.randn(len(speech)) * 0.01
        
        # Save as WAV
        wavfile.write(filename, sample_rate, (speech * 32767).astype(np.int16))
        logger.info(f"Generated synthetic speech file: {filename}")


def load_audio_file(filename: str, target_sample_rate: int = 16000) -> np.ndarray:
    """Load audio file and convert to float32"""
    sample_rate, audio = wavfile.read(filename)
    
    # Convert to float32
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0
    elif audio.dtype == np.int32:
        audio = audio.astype(np.float32) / 2147483648.0
    else:
        audio = audio.astype(np.float32)
    
    # Resample if needed
    if sample_rate != target_sample_rate:
        from scipy import signal
        audio = signal.resample(audio, int(len(audio) * target_sample_rate / sample_rate))
    
    return audio


async def test_parakeet_with_files():
    """Test Parakeet STT with various audio files"""
    # Test phrases
    test_phrases = [
        "Hello world, this is a test of the speech recognition system.",
        "The quick brown fox jumps over the lazy dog.",
        "Personal Parakeet is a real-time dictation tool.",
        "Testing one two three, can you hear me clearly?",
        "This is a longer sentence to test how well the model handles continuous speech with multiple words and phrases."
    ]
    
    # Create test directory
    test_dir = Path("test_audio")
    test_dir.mkdir(exist_ok=True)
    
    # Generate test files
    test_files = []
    for i, phrase in enumerate(test_phrases):
        filename = test_dir / f"test_{i}.wav"
        generate_test_speech(phrase, str(filename))
        test_files.append((filename, phrase))
    
    # Initialize STT
    config = V3Config()
    stt_processor = STTFactory.create_stt_processor(config)
    await stt_processor.initialize()
    
    logger.info("\n" + "="*60)
    logger.info("Testing Parakeet STT with audio files")
    logger.info("="*60)
    
    # Test each file
    for audio_file, expected_text in test_files:
        logger.info(f"\nTesting: {audio_file.name}")
        logger.info(f"Expected: {expected_text}")
        
        # Load audio
        audio = load_audio_file(str(audio_file))
        logger.info(f"Audio shape: {audio.shape}, duration: {len(audio)/16000:.2f}s")
        
        # Transcribe full audio
        result = stt_processor.transcribe(audio)
        logger.info(f"Result: {result}")
        
        if result:
            # Simple accuracy check (word overlap)
            expected_words = set(expected_text.lower().split())
            result_words = set(result.lower().split())
            overlap = len(expected_words & result_words) / len(expected_words)
            logger.info(f"Word accuracy: {overlap*100:.1f}%")
    
    # Test streaming mode (chunks)
    logger.info("\n" + "="*60)
    logger.info("Testing streaming mode with chunks")
    logger.info("="*60)
    
    # Use a longer audio file for streaming test
    long_text = " ".join(test_phrases)
    long_file = test_dir / "long_test.wav"
    generate_test_speech(long_text, str(long_file))
    
    audio = load_audio_file(str(long_file))
    chunk_size = int(0.5 * 16000)  # 0.5 second chunks
    
    logger.info(f"Audio duration: {len(audio)/16000:.2f}s")
    logger.info(f"Chunk size: {chunk_size/16000:.2f}s")
    
    # Process in chunks
    results = []
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i+chunk_size]
        if len(chunk) < chunk_size * 0.5:  # Skip very short last chunk
            break
            
        logger.info(f"\nChunk {i//chunk_size + 1}: {len(chunk)/16000:.2f}s")
        result = stt_processor.transcribe(chunk)
        logger.info(f"Result: {result}")
        if result:
            results.append(result)
    
    logger.info(f"\nTotal chunks transcribed: {len(results)}")
    logger.info(f"Full transcription: {' '.join(results)}")
    
    # Cleanup
    await stt_processor.cleanup()
    
    # Remove test files
    import shutil
    shutil.rmtree(test_dir)


async def test_parakeet_realtime_simulation():
    """Simulate realtime audio capture and transcription"""
    logger.info("\n" + "="*60)
    logger.info("Testing realtime simulation")
    logger.info("="*60)
    
    # Initialize STT
    config = V3Config()
    stt_processor = STTFactory.create_stt_processor(config)
    await stt_processor.initialize()
    
    # Generate continuous speech
    text = "This is a simulation of real time speech recognition where we process audio in small chunks as it arrives from the microphone"
    audio_file = "realtime_test.wav"
    generate_test_speech(text, audio_file)
    
    # Load full audio
    audio = load_audio_file(audio_file)
    
    # Simulate realtime capture (100ms chunks)
    chunk_duration = 0.1  # 100ms
    chunk_size = int(chunk_duration * 16000)
    
    logger.info(f"Simulating realtime capture with {chunk_duration*1000:.0f}ms chunks")
    
    buffer = []
    process_size = int(0.5 * 16000)  # Process every 0.5s
    
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i+chunk_size]
        buffer.extend(chunk)
        
        # Process when buffer is large enough
        if len(buffer) >= process_size:
            process_chunk = np.array(buffer[:process_size])
            buffer = buffer[process_size:]
            
            result = stt_processor.transcribe(process_chunk)
            if result:
                logger.info(f"[{i/16000:.1f}s] Transcribed: {result}")
        
        # Simulate realtime delay
        await asyncio.sleep(chunk_duration * 0.5)  # Run at 2x speed
    
    # Process remaining buffer
    if buffer:
        result = stt_processor.transcribe(np.array(buffer))
        if result:
            logger.info(f"[Final] Transcribed: {result}")
    
    # Cleanup
    await stt_processor.cleanup()
    os.remove(audio_file)


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_parakeet_with_files())
    asyncio.run(test_parakeet_realtime_simulation())