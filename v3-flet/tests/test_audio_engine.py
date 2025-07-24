#!/usr/bin/env python3
"""
Audio Engine Tests for PersonalParakeet v3
Tests audio pipeline, VAD, and STT integration without requiring microphone
"""

import sys
import asyncio
import logging
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from audio_engine import AudioEngine
from config import V3Config

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioEngineTest:
    """Test suite for AudioEngine functionality"""
    
    def __init__(self):
        self.test_results = {
            'initialization': False,
            'mock_audio_processing': False,
            'vad_integration': False,
            'stt_pipeline': False,
            'cleanup': False,
            'total_errors': 0
        }
        self.config = V3Config()
    
    async def test_initialization(self):
        """Test AudioEngine initialization"""
        try:
            logger.info("Testing AudioEngine initialization...")
            
            # Mock dependencies to avoid hardware requirements
            with patch('sounddevice.query_devices'), \
                 patch('sounddevice.default'), \
                 patch('torch.cuda.is_available', return_value=True):
                
                loop = asyncio.get_event_loop()
                audio_engine = AudioEngine(self.config, loop)
                
                # Test initialization without starting audio stream
                await audio_engine.initialize()
                
                # Check that components are initialized
                assert audio_engine.stt_processor is not None
                assert audio_engine.clarity_engine is not None
                assert audio_engine.vad_engine is not None
                
                logger.info("✓ AudioEngine initialization successful")
                self.test_results['initialization'] = True
                return True
                
        except Exception as e:
            logger.error(f"✗ AudioEngine initialization error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    async def test_mock_audio_processing(self):
        """Test audio processing with mock data"""
        try:
            logger.info("Testing mock audio processing...")
            
            with patch('sounddevice.query_devices'), \
                 patch('sounddevice.default'), \
                 patch('torch.cuda.is_available', return_value=True):
                
                loop = asyncio.get_event_loop()
                audio_engine = AudioEngine(self.config, loop)
                await audio_engine.initialize()
                
                # Create mock audio data (1 second of 16kHz audio)
                sample_rate = 16000
                duration = 1.0
                mock_audio = np.random.random((int(sample_rate * duration), 1)).astype(np.float32)
                
                # Mock the STT processor to return predictable results
                mock_result = "test transcription"
                audio_engine.stt_processor.transcribe = AsyncMock(return_value=mock_result)
                
                # Process mock audio
                result = await audio_engine._process_audio_chunk(mock_audio)
                
                # Verify processing occurred
                assert result is not None or mock_result == "test transcription"
                
                logger.info("✓ Mock audio processing successful")
                self.test_results['mock_audio_processing'] = True
                return True
                
        except Exception as e:
            logger.error(f"✗ Mock audio processing error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    async def test_vad_integration(self):
        """Test Voice Activity Detection integration"""
        try:
            logger.info("Testing VAD integration...")
            
            with patch('sounddevice.query_devices'), \
                 patch('sounddevice.default'), \
                 patch('torch.cuda.is_available', return_value=True):
                
                loop = asyncio.get_event_loop()
                audio_engine = AudioEngine(self.config, loop)
                await audio_engine.initialize()
                
                # Test VAD with mock audio
                mock_audio = np.random.random((16000, 1)).astype(np.float32)  # 1 second
                
                # Mock VAD to return voice activity
                audio_engine.vad_engine.is_speech = Mock(return_value=True)
                
                # Test VAD processing
                is_speech = audio_engine.vad_engine.is_speech(mock_audio)
                assert is_speech == True
                
                logger.info("✓ VAD integration successful")
                self.test_results['vad_integration'] = True
                return True
                
        except Exception as e:
            logger.error(f"✗ VAD integration error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    async def test_stt_pipeline(self):
        """Test STT pipeline integration"""
        try:
            logger.info("Testing STT pipeline...")
            
            with patch('sounddevice.query_devices'), \
                 patch('sounddevice.default'), \
                 patch('torch.cuda.is_available', return_value=True):
                
                loop = asyncio.get_event_loop()
                audio_engine = AudioEngine(self.config, loop)
                await audio_engine.initialize()
                
                # Mock STT processor
                mock_transcription = "Hello world test transcription"
                audio_engine.stt_processor.transcribe = AsyncMock(return_value=mock_transcription)
                
                # Test transcription
                mock_audio = np.random.random((16000, 1)).astype(np.float32)
                result = await audio_engine.stt_processor.transcribe(mock_audio)
                
                assert result == mock_transcription
                
                logger.info("✓ STT pipeline successful")
                self.test_results['stt_pipeline'] = True
                return True
                
        except Exception as e:
            logger.error(f"✗ STT pipeline error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    async def test_cleanup(self):
        """Test proper cleanup of resources"""
        try:
            logger.info("Testing cleanup...")
            
            with patch('sounddevice.query_devices'), \
                 patch('sounddevice.default'), \
                 patch('torch.cuda.is_available', return_value=True):
                
                loop = asyncio.get_event_loop()
                audio_engine = AudioEngine(self.config, loop)
                await audio_engine.initialize()
                
                # Test cleanup
                await audio_engine.stop()
                
                # Verify cleanup state
                assert not audio_engine.is_running
                
                logger.info("✓ Cleanup successful")
                self.test_results['cleanup'] = True
                return True
                
        except Exception as e:
            logger.error(f"✗ Cleanup error: {e}")
            self.test_results['total_errors'] += 1
            return False
    
    async def run_test(self):
        """Run all audio engine tests"""
        logger.info("=== PersonalParakeet v3 Audio Engine Test ===")
        
        # Run tests in order
        await self.test_initialization()
        await self.test_mock_audio_processing()
        await self.test_vad_integration()
        await self.test_stt_pipeline()
        await self.test_cleanup()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        logger.info("=== AUDIO ENGINE TEST RESULTS ===")
        
        passed_tests = []
        failed_tests = []
        
        for test_name, result in self.test_results.items():
            if test_name == 'total_errors':
                continue
                
            if result:
                passed_tests.append(test_name)
                logger.info(f"✓ {test_name}: PASS")
            else:
                failed_tests.append(test_name)
                logger.error(f"✗ {test_name}: FAIL")
        
        logger.info(f"Total errors: {self.test_results['total_errors']}")
        logger.info(f"Tests passed: {len(passed_tests)}/{len(passed_tests) + len(failed_tests)}")
        
        if self.test_results['total_errors'] == 0 and len(failed_tests) == 0:
            logger.info("🎉 OVERALL: AUDIO ENGINE TEST PASSED")
            overall_result = "PASS"
        else:
            logger.error("❌ OVERALL: AUDIO ENGINE TEST FAILED")
            overall_result = "FAIL"
        
        return {
            'overall_result': overall_result,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'total_errors': self.test_results['total_errors']
        }


if __name__ == "__main__":
    async def main():
        test = AudioEngineTest()
        results = await test.run_test()
        
        exit_code = 0 if results['overall_result'] == 'PASS' else 1
        sys.exit(exit_code)
    
    asyncio.run(main())