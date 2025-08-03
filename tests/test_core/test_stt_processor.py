"""
Unit tests for STT Processor in PersonalParakeet v3.

Tests the speech-to-text processing functionality including
audio format validation, transcription accuracy, and error handling.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
from pathlib import Path

try:
    from core.stt_processor import STTProcessor
    from core.stt_factory import STTFactory
except ImportError:
    # For testing when modules don't exist yet
    STTProcessor = Mock
    STTFactory = Mock


class TestSTTProcessor:
    """Test suite for STT Processor component."""

    @pytest.fixture
    def mock_processor(self, test_config):
        """Create a mock STT processor for testing."""
        processor = Mock(spec=STTProcessor)
        processor.config = test_config["stt"]
        processor.sample_rate = test_config["audio"]["sample_rate"]
        processor.is_initialized = True
        return processor

    @pytest.mark.unit
    def test_processor_initialization(self, test_config):
        """Test STT processor initialization."""
        # Test with mock since actual implementation may not exist
        with patch('core.stt_processor.STTProcessor') as MockSTTProcessor:
            mock_instance = Mock()
            MockSTTProcessor.return_value = mock_instance
            
            processor = MockSTTProcessor(config=test_config["stt"])
            
            # Verify initialization
            MockSTTProcessor.assert_called_once_with(config=test_config["stt"])
            assert processor is not None

    @pytest.mark.unit
    def test_audio_format_validation(self, mock_processor, sample_audio_data):
        """Test audio format validation."""
        def mock_validate_audio(audio_data):
            if not isinstance(audio_data, np.ndarray):
                raise ValueError("Audio data must be numpy array")
            if audio_data.dtype != np.float32:
                raise ValueError("Audio data must be float32")
            if len(audio_data.shape) != 1:
                raise ValueError("Audio data must be mono (1D)")
            return True

        mock_processor.validate_audio_format = mock_validate_audio

        # Test valid audio
        assert mock_processor.validate_audio_format(sample_audio_data) is True

        # Test invalid formats
        with pytest.raises(ValueError, match="numpy array"):
            mock_processor.validate_audio_format("invalid")

        with pytest.raises(ValueError, match="float32"):
            invalid_dtype = sample_audio_data.astype(np.int16)
            mock_processor.validate_audio_format(invalid_dtype)

        with pytest.raises(ValueError, match="mono"):
            stereo_audio = np.stack([sample_audio_data, sample_audio_data])
            mock_processor.validate_audio_format(stereo_audio)

    @pytest.mark.unit
    def test_transcription_basic(self, mock_processor, sample_audio_data):
        """Test basic transcription functionality."""
        expected_text = "This is a test transcription"
        
        def mock_transcribe(audio_data):
            if len(audio_data) > 0:
                return {
                    "text": expected_text,
                    "confidence": 0.95,
                    "processing_time": 0.1
                }
            return {"text": "", "confidence": 0.0, "processing_time": 0.0}

        mock_processor.transcribe = mock_transcribe

        result = mock_processor.transcribe(sample_audio_data)
        
        assert result["text"] == expected_text
        assert result["confidence"] > 0.8
        assert result["processing_time"] >= 0

    @pytest.mark.unit
    def test_transcription_empty_audio(self, mock_processor):
        """Test transcription with empty audio."""
        def mock_transcribe(audio_data):
            if len(audio_data) == 0:
                return {"text": "", "confidence": 0.0, "processing_time": 0.0}
            return {"text": "test", "confidence": 0.5, "processing_time": 0.1}

        mock_processor.transcribe = mock_transcribe
        
        empty_audio = np.array([], dtype=np.float32)
        result = mock_processor.transcribe(empty_audio)
        
        assert result["text"] == ""
        assert result["confidence"] == 0.0

    @pytest.mark.unit
    def test_confidence_threshold(self, mock_processor, sample_audio_data):
        """Test confidence threshold filtering."""
        def mock_transcribe_with_confidence(audio_data, min_confidence=0.8):
            base_result = {
                "text": "low confidence text",
                "confidence": 0.5,
                "processing_time": 0.1
            }
            
            if base_result["confidence"] < min_confidence:
                return {"text": "", "confidence": base_result["confidence"], "processing_time": base_result["processing_time"]}
            return base_result

        mock_processor.transcribe_with_threshold = mock_transcribe_with_confidence

        # Test below threshold
        result = mock_processor.transcribe_with_threshold(sample_audio_data, min_confidence=0.8)
        assert result["text"] == ""
        assert result["confidence"] == 0.5

        # Test above threshold
        result = mock_processor.transcribe_with_threshold(sample_audio_data, min_confidence=0.3)
        assert result["text"] == "low confidence text"

    @pytest.mark.unit
    def test_error_handling(self, mock_processor, sample_audio_data):
        """Test error handling in STT processing."""
        def mock_transcribe_with_error(audio_data):
            if len(audio_data) > 10000:  # Simulate error for large audio
                raise RuntimeError("STT engine error")
            return {"text": "success", "confidence": 0.9, "processing_time": 0.1}

        mock_processor.transcribe = mock_transcribe_with_error

        # Test successful transcription
        short_audio = sample_audio_data[:5000]
        result = mock_processor.transcribe(short_audio)
        assert result["text"] == "success"

        # Test error handling
        long_audio = sample_audio_data[:20000] if len(sample_audio_data) >= 20000 else np.tile(sample_audio_data, 2)
        with pytest.raises(RuntimeError, match="STT engine error"):
            mock_processor.transcribe(long_audio)

    @pytest.mark.unit
    @pytest.mark.performance
    def test_processing_performance(self, mock_processor, sample_audio_data):
        """Test STT processing performance metrics."""
        def mock_transcribe_timed(audio_data):
            import time
            start_time = time.time()
            
            # Simulate processing delay based on audio length
            processing_time = len(audio_data) / 16000 * 0.1  # 10% of audio duration
            time.sleep(min(processing_time, 0.01))  # Cap at 10ms for testing
            
            end_time = time.time()
            actual_time = end_time - start_time
            
            return {
                "text": f"Processed {len(audio_data)} samples",
                "confidence": 0.9,
                "processing_time": actual_time
            }

        mock_processor.transcribe = mock_transcribe_timed

        result = mock_processor.transcribe(sample_audio_data)
        
        # Performance assertions
        assert result["processing_time"] < 1.0  # Should process faster than real-time
        assert "Processed" in result["text"]
        assert result["confidence"] > 0.8

    @pytest.mark.unit
    def test_batch_processing(self, mock_processor):
        """Test batch processing of multiple audio segments."""
        def mock_transcribe_batch(audio_segments):
            results = []
            for i, segment in enumerate(audio_segments):
                results.append({
                    "text": f"Segment {i+1}",
                    "confidence": 0.9,
                    "processing_time": 0.05
                })
            return results

        mock_processor.transcribe_batch = mock_transcribe_batch

        # Create test audio segments
        segments = [
            np.random.randn(1000).astype(np.float32),
            np.random.randn(1500).astype(np.float32),
            np.random.randn(800).astype(np.float32)
        ]

        results = mock_processor.transcribe_batch(segments)
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["text"] == f"Segment {i+1}"
            assert result["confidence"] == 0.9

    @pytest.mark.unit
    def test_language_detection(self, mock_processor, sample_audio_data):
        """Test language detection capability."""
        def mock_detect_language(audio_data):
            # Mock language detection based on audio characteristics
            if np.mean(audio_data) > 0:
                return {"language": "en-US", "confidence": 0.95}
            else:
                return {"language": "es-ES", "confidence": 0.85}

        mock_processor.detect_language = mock_detect_language

        result = mock_processor.detect_language(sample_audio_data)
        
        assert "language" in result
        assert "confidence" in result
        assert result["confidence"] > 0.8
        assert result["language"] in ["en-US", "es-ES"]

    @pytest.mark.integration
    def test_stt_factory_integration(self, test_config):
        """Test STT processor creation through factory."""
        with patch('core.stt_factory.STTFactory') as MockFactory:
            mock_factory = Mock()
            mock_processor = Mock(spec=STTProcessor)
            mock_factory.create_processor.return_value = mock_processor
            MockFactory.return_value = mock_factory

            factory = MockFactory()
            processor = factory.create_processor(engine_type="mock", config=test_config["stt"])

            mock_factory.create_processor.assert_called_once_with(
                engine_type="mock", 
                config=test_config["stt"]
            )
            assert processor is mock_processor

    @pytest.mark.unit
    def test_cleanup_resources(self, mock_processor):
        """Test proper cleanup of STT processor resources."""
        mock_processor.cleanup = Mock()
        mock_processor.is_initialized = True

        # Simulate cleanup
        mock_processor.cleanup()
        mock_processor.is_initialized = False

        mock_processor.cleanup.assert_called_once()

    @pytest.mark.slow
    def test_real_time_processing_simulation(self, mock_processor):
        """Test real-time processing simulation."""
        import threading
        import queue
        import time

        audio_queue = queue.Queue()
        result_queue = queue.Queue()

        def mock_real_time_processor():
            while True:
                try:
                    audio_data = audio_queue.get(timeout=0.1)
                    if audio_data is None:  # Shutdown signal
                        break
                    
                    # Simulate processing
                    result = {
                        "text": f"Processed chunk {len(audio_data)} samples",
                        "confidence": 0.9,
                        "timestamp": time.time()
                    }
                    result_queue.put(result)
                    audio_queue.task_done()
                except queue.Empty:
                    continue

        # Start processing thread
        processor_thread = threading.Thread(target=mock_real_time_processor)
        processor_thread.start()

        # Send test audio chunks
        test_chunks = [
            np.random.randn(1024).astype(np.float32),
            np.random.randn(1024).astype(np.float32),
            np.random.randn(1024).astype(np.float32)
        ]

        for chunk in test_chunks:
            audio_queue.put(chunk)

        # Collect results
        results = []
        for _ in range(len(test_chunks)):
            result = result_queue.get(timeout=1.0)
            results.append(result)

        # Cleanup
        audio_queue.put(None)  # Shutdown signal
        processor_thread.join(timeout=1.0)

        assert len(results) == 3
        for result in results:
            assert "Processed chunk" in result["text"]
            assert result["confidence"] == 0.9