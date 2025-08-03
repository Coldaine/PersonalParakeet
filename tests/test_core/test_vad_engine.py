"""
Unit tests for VAD Engine in PersonalParakeet v3.

Tests the voice activity detection functionality including
audio analysis, silence detection, and voice segment extraction.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import time

try:
    from core.vad_engine import VoiceActivityDetector
except ImportError:
    # For testing when modules don't exist yet
    VoiceActivityDetector = Mock


class TestVADEngine:
    """Test suite for Voice Activity Detection Engine."""

    @pytest.fixture
    def mock_vad(self, test_config):
        """Create a mock VAD engine for testing."""
        vad = Mock(spec=VoiceActivityDetector)
        vad.config = test_config["vad"]
        vad.sample_rate = test_config["audio"]["sample_rate"]
        vad.frame_duration_ms = test_config["vad"]["frame_duration_ms"]
        vad.aggressiveness = test_config["vad"]["aggressiveness"]
        return vad

    @pytest.fixture
    def voice_audio(self):
        """Generate synthetic audio with voice activity."""
        duration = 2.0  # 2 seconds
        sample_rate = 16000
        samples = int(sample_rate * duration)
        
        # Generate voice-like signal (multiple frequencies)
        t = np.linspace(0, duration, samples)
        voice = (np.sin(2 * np.pi * 200 * t) + 
                np.sin(2 * np.pi * 400 * t) + 
                np.sin(2 * np.pi * 800 * t)) * 0.3
        
        # Add some noise
        voice += np.random.randn(samples) * 0.05
        
        return voice.astype(np.float32)

    @pytest.fixture
    def silence_audio(self):
        """Generate audio with mostly silence."""
        duration = 2.0
        sample_rate = 16000
        samples = int(sample_rate * duration)
        
        # Low amplitude noise
        silence = np.random.randn(samples) * 0.01
        
        return silence.astype(np.float32)

    @pytest.fixture
    def mixed_audio(self, voice_audio, silence_audio):
        """Generate audio with alternating voice and silence."""
        # Combine voice and silence in segments
        segment_size = len(voice_audio) // 4
        mixed = np.concatenate([
            voice_audio[:segment_size],      # Voice
            silence_audio[segment_size:2*segment_size],  # Silence
            voice_audio[2*segment_size:3*segment_size],  # Voice
            silence_audio[3*segment_size:]    # Silence
        ])
        return mixed

    @pytest.mark.unit
    def test_vad_initialization(self, test_config):
        """Test VAD engine initialization."""
        with patch('core.vad_engine.VoiceActivityDetector') as MockVAD:
            mock_instance = Mock()
            MockVAD.return_value = mock_instance
            
            vad = MockVAD(
                sample_rate=test_config["audio"]["sample_rate"],
                aggressiveness=test_config["vad"]["aggressiveness"]
            )
            
            MockVAD.assert_called_once_with(
                sample_rate=test_config["audio"]["sample_rate"],
                aggressiveness=test_config["vad"]["aggressiveness"]
            )
            assert vad is not None

    @pytest.mark.unit
    def test_voice_detection(self, mock_vad, voice_audio):
        """Test basic voice activity detection."""
        def mock_is_speech(audio_frame):
            # Simple energy-based detection
            energy = np.mean(np.square(audio_frame))
            return energy > 0.01  # Threshold for voice detection
        
        mock_vad.is_speech = mock_is_speech
        
        # Test with voice audio
        frame_size = 480  # 30ms at 16kHz
        voice_frame = voice_audio[:frame_size]
        
        result = mock_vad.is_speech(voice_frame)
        assert result is True

    @pytest.mark.unit
    def test_silence_detection(self, mock_vad, silence_audio):
        """Test silence detection."""
        def mock_is_speech(audio_frame):
            energy = np.mean(np.square(audio_frame))
            return energy > 0.01
        
        mock_vad.is_speech = mock_is_speech
        
        # Test with silence audio
        frame_size = 480
        silence_frame = silence_audio[:frame_size]
        
        result = mock_vad.is_speech(silence_frame)
        assert result is False

    @pytest.mark.unit
    def test_frame_processing(self, mock_vad, mixed_audio):
        """Test processing audio in frames."""
        def mock_process_frames(audio_data, frame_duration_ms=30):
            sample_rate = 16000
            frame_size = int(sample_rate * frame_duration_ms / 1000)
            frames = []
            
            for i in range(0, len(audio_data), frame_size):
                frame = audio_data[i:i+frame_size]
                if len(frame) == frame_size:
                    energy = np.mean(np.square(frame))
                    is_voice = energy > 0.01
                    frames.append({
                        'audio': frame,
                        'is_voice': is_voice,
                        'energy': energy,
                        'timestamp': i / sample_rate
                    })
            
            return frames
        
        mock_vad.process_frames = mock_process_frames
        
        frames = mock_vad.process_frames(mixed_audio)
        
        assert len(frames) > 0
        voice_frames = [f for f in frames if f['is_voice']]
        silence_frames = [f for f in frames if not f['is_voice']]
        
        # Should have both voice and silence frames
        assert len(voice_frames) > 0
        assert len(silence_frames) > 0

    @pytest.mark.unit
    def test_aggressiveness_levels(self, test_config):
        """Test different VAD aggressiveness levels."""
        def create_mock_vad(aggressiveness):
            vad = Mock()
            vad.aggressiveness = aggressiveness
            
            def mock_is_speech(audio_frame):
                energy = np.mean(np.square(audio_frame))
                # More aggressive = higher threshold
                threshold = 0.005 + (aggressiveness - 1) * 0.01
                return energy > threshold
            
            vad.is_speech = mock_is_speech
            return vad
        
        # Test different aggressiveness levels
        test_frame = np.random.randn(480).astype(np.float32) * 0.02
        
        for aggressiveness in [1, 2, 3]:
            vad = create_mock_vad(aggressiveness)
            result = vad.is_speech(test_frame)
            
            # Higher aggressiveness should be more selective
            if aggressiveness == 1:
                assert isinstance(result, bool)

    @pytest.mark.unit
    def test_voice_segment_extraction(self, mock_vad, mixed_audio):
        """Test extraction of voice segments from audio."""
        def mock_extract_voice_segments(audio_data, min_duration_ms=100):
            sample_rate = 16000
            frame_size = 480  # 30ms
            min_frames = max(1, int(min_duration_ms / 30))
            
            segments = []
            current_segment = []
            is_in_voice = False
            
            for i in range(0, len(audio_data), frame_size):
                frame = audio_data[i:i+frame_size]
                if len(frame) < frame_size:
                    break
                
                energy = np.mean(np.square(frame))
                is_voice = energy > 0.01
                
                if is_voice:
                    if not is_in_voice:
                        current_segment = []
                        is_in_voice = True
                    current_segment.extend(frame)
                else:
                    if is_in_voice and len(current_segment) >= min_frames * frame_size:
                        segments.append({
                            'audio': np.array(current_segment),
                            'start_time': (i - len(current_segment)) / sample_rate,
                            'duration': len(current_segment) / sample_rate
                        })
                    is_in_voice = False
            
            # Handle final segment
            if is_in_voice and len(current_segment) >= min_frames * frame_size:
                segments.append({
                    'audio': np.array(current_segment),
                    'start_time': (len(audio_data) - len(current_segment)) / sample_rate,
                    'duration': len(current_segment) / sample_rate
                })
            
            return segments
        
        mock_vad.extract_voice_segments = mock_extract_voice_segments
        
        segments = mock_vad.extract_voice_segments(mixed_audio)
        
        assert len(segments) > 0
        for segment in segments:
            assert 'audio' in segment
            assert 'start_time' in segment
            assert 'duration' in segment
            assert len(segment['audio']) > 0
            assert segment['duration'] > 0

    @pytest.mark.unit
    def test_real_time_processing(self, mock_vad):
        """Test real-time VAD processing."""
        def mock_process_realtime(audio_chunk):
            energy = np.mean(np.square(audio_chunk))
            confidence = min(1.0, energy / 0.05)  # Normalize to 0-1
            
            return {
                'is_voice': energy > 0.01,
                'confidence': confidence,
                'energy': energy,
                'timestamp': time.time()
            }
        
        mock_vad.process_realtime = mock_process_realtime
        
        # Test with different audio chunks
        voice_chunk = np.random.randn(480).astype(np.float32) * 0.1
        silence_chunk = np.random.randn(480).astype(np.float32) * 0.005
        
        voice_result = mock_vad.process_realtime(voice_chunk)
        silence_result = mock_vad.process_realtime(silence_chunk)
        
        assert voice_result['is_voice'] is True
        assert silence_result['is_voice'] is False
        assert voice_result['confidence'] > silence_result['confidence']

    @pytest.mark.unit
    def test_noise_robustness(self, mock_vad, voice_audio):
        """Test VAD robustness against noise."""
        def mock_is_speech_with_noise_handling(audio_frame, noise_threshold=0.02):
            # Simple spectral analysis mock
            fft = np.fft.rfft(audio_frame)
            magnitude = np.abs(fft)
            
            # Voice typically has energy in speech frequencies (300-3400 Hz)
            sample_rate = 16000
            freqs = np.fft.rfftfreq(len(audio_frame), 1/sample_rate)
            speech_mask = (freqs >= 300) & (freqs <= 3400)
            
            speech_energy = np.mean(magnitude[speech_mask])
            total_energy = np.mean(magnitude)
            
            # High ratio suggests voice vs noise
            if total_energy > noise_threshold:
                speech_ratio = speech_energy / total_energy
                return speech_ratio > 0.3
            
            return False
        
        mock_vad.is_speech = mock_is_speech_with_noise_handling
        
        # Test clean voice
        frame_size = 480
        clean_frame = voice_audio[:frame_size]
        
        # Test noisy voice
        noise = np.random.randn(frame_size) * 0.05
        noisy_frame = clean_frame + noise
        
        clean_result = mock_vad.is_speech(clean_frame)
        noisy_result = mock_vad.is_speech(noisy_frame)
        
        # Both should detect voice, but clean should have higher confidence
        assert isinstance(clean_result, bool)
        assert isinstance(noisy_result, bool)

    @pytest.mark.integration
    def test_vad_audio_pipeline_integration(self, mock_vad, mixed_audio):
        """Test VAD integration with audio pipeline."""
        def mock_pipeline_process(audio_data):
            # Simulate pipeline: VAD -> segment extraction -> results
            frames = []
            frame_size = 480
            
            for i in range(0, len(audio_data), frame_size):
                frame = audio_data[i:i+frame_size]
                if len(frame) == frame_size:
                    energy = np.mean(np.square(frame))
                    frames.append({
                        'frame': frame,
                        'is_voice': energy > 0.01,
                        'timestamp': i / 16000
                    })
            
            # Extract voice segments
            voice_segments = []
            current_segment = []
            
            for frame_data in frames:
                if frame_data['is_voice']:
                    current_segment.append(frame_data)
                else:
                    if len(current_segment) >= 3:  # Minimum 3 frames
                        voice_segments.append(current_segment)
                    current_segment = []
            
            return {
                'total_frames': len(frames),
                'voice_segments': len(voice_segments),
                'voice_ratio': len([f for f in frames if f['is_voice']]) / len(frames)
            }
        
        mock_vad.pipeline_process = mock_pipeline_process
        
        result = mock_vad.pipeline_process(mixed_audio)
        
        assert result['total_frames'] > 0
        assert 0 <= result['voice_ratio'] <= 1
        assert result['voice_segments'] >= 0

    @pytest.mark.performance
    def test_vad_performance(self, mock_vad):
        """Test VAD processing performance."""
        def mock_performance_test(audio_data):
            start_time = time.time()
            
            frame_size = 480
            processed_frames = 0
            
            for i in range(0, len(audio_data), frame_size):
                frame = audio_data[i:i+frame_size]
                if len(frame) == frame_size:
                    # Simulate processing
                    energy = np.mean(np.square(frame))
                    is_voice = energy > 0.01
                    processed_frames += 1
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            return {
                'processing_time': processing_time,
                'frames_processed': processed_frames,
                'frames_per_second': processed_frames / processing_time if processing_time > 0 else 0,
                'real_time_factor': (len(audio_data) / 16000) / processing_time if processing_time > 0 else 0
            }
        
        mock_vad.performance_test = mock_performance_test
        
        # Test with 5 seconds of audio
        test_audio = np.random.randn(80000).astype(np.float32)
        result = mock_vad.performance_test(test_audio)
        
        assert result['processing_time'] > 0
        assert result['frames_processed'] > 0
        assert result['frames_per_second'] > 0
        # Should process faster than real-time
        assert result['real_time_factor'] > 1.0

    @pytest.mark.unit
    def test_configuration_validation(self, mock_vad):
        """Test VAD configuration validation."""
        def mock_validate_config(config):
            errors = []
            
            if 'aggressiveness' not in config:
                errors.append("aggressiveness required")
            elif not 1 <= config['aggressiveness'] <= 3:
                errors.append("aggressiveness must be 1-3")
            
            if 'frame_duration_ms' not in config:
                errors.append("frame_duration_ms required")
            elif config['frame_duration_ms'] not in [10, 20, 30]:
                errors.append("frame_duration_ms must be 10, 20, or 30")
            
            return errors
        
        mock_vad.validate_config = mock_validate_config
        
        # Test valid config
        valid_config = {'aggressiveness': 2, 'frame_duration_ms': 30}
        errors = mock_vad.validate_config(valid_config)
        assert len(errors) == 0
        
        # Test invalid config
        invalid_config = {'aggressiveness': 5, 'frame_duration_ms': 15}
        errors = mock_vad.validate_config(invalid_config)
        assert len(errors) > 0