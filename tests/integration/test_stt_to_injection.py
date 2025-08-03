"""Test STT output to text injection pipeline."""

import platform
import time
from unittest.mock import MagicMock, patch

import pytest

from tests.core import BaseHardwareTest


class TestSTTToInjection(BaseHardwareTest):
    """Test speech-to-text output to text injection."""
    
    @pytest.mark.integration
    def test_text_injection_simulation(self):
        """Test text injection simulation (without actual keyboard events)."""
        # Simulate STT output
        stt_outputs = [
            "Hello world",
            "This is a test",
            "Testing punctuation, periods, and questions?",
            "Numbers like 123 and symbols @#$"
        ]
        
        # Mock injection results
        injected_texts = []
        injection_times = []
        
        def mock_inject_text(text: str):
            """Simulate text injection."""
            start = time.time()
            # Simulate typing delay (10ms per character)
            time.sleep(len(text) * 0.01)
            injected_texts.append(text)
            injection_times.append(time.time() - start)
        
        # Process STT outputs
        print("\nSimulating text injection:")
        for text in stt_outputs:
            print(f"  Injecting: '{text}'")
            mock_inject_text(text)
        
        # Verify results
        assert len(injected_texts) == len(stt_outputs)
        assert injected_texts == stt_outputs
        
        # Check injection timing
        avg_time = sum(injection_times) / len(injection_times)
        print(f"\nInjection timing:")
        print(f"  Average: {avg_time*1000:.1f} ms")
        print(f"  Total: {sum(injection_times)*1000:.1f} ms")
    
    @pytest.mark.integration
    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
    def test_windows_injection_setup(self):
        """Test Windows text injection setup."""
        try:
            import pyautogui
            
            # Test pyautogui availability
            print("\nPyautogui configuration:")
            print(f"  Failsafe: {pyautogui.FAILSAFE}")
            print(f"  Pause: {pyautogui.PAUSE}")
            
            # Get screen size
            width, height = pyautogui.size()
            print(f"  Screen: {width}x{height}")
            
            # Test position
            x, y = pyautogui.position()
            print(f"  Mouse position: ({x}, {y})")
            
            assert width > 0 and height > 0, "Invalid screen size"
            
        except ImportError:
            pytest.skip("pyautogui not installed")
        except Exception as e:
            pytest.skip(f"pyautogui not available: {e}")
    
    @pytest.mark.integration
    def test_text_preprocessing_for_injection(self):
        """Test text preprocessing before injection."""
        test_cases = [
            # (input, expected_output)
            ("hello world", "hello world"),
            ("HELLO WORLD", "HELLO WORLD"),
            ("hello\nworld", "hello world"),  # Newlines to spaces
            ("hello\tworld", "hello world"),  # Tabs to spaces
            ("hello  world", "hello world"),  # Multiple spaces
            ("  hello world  ", "hello world"),  # Trim
            ("hello—world", "hello--world"),  # Em dash to double dash
            ("hello'world", "hello'world"),  # Smart quotes
        ]
        
        def preprocess_for_injection(text: str) -> str:
            """Preprocess text for injection."""
            # Replace newlines and tabs with spaces
            text = text.replace('\n', ' ').replace('\t', ' ')
            # Collapse multiple spaces
            while '  ' in text:
                text = text.replace('  ', ' ')
            # Trim
            text = text.strip()
            # Handle special characters
            text = text.replace('—', '--')
            return text
        
        print("\nText preprocessing:")
        for input_text, expected in test_cases:
            processed = preprocess_for_injection(input_text)
            print(f"  '{input_text}' -> '{processed}'")
            assert processed == expected, f"Expected '{expected}', got '{processed}'"
    
    @pytest.mark.integration
    def test_injection_queue_handling(self):
        """Test handling of text injection queue."""
        import queue
        import threading
        
        # Create injection queue
        injection_queue = queue.Queue()
        injected_texts = []
        
        def injection_worker():
            """Worker thread for text injection."""
            while True:
                item = injection_queue.get()
                if item is None:
                    break
                
                # Simulate injection with delay
                time.sleep(0.05)
                injected_texts.append(item)
                injection_queue.task_done()
        
        # Start worker
        worker = threading.Thread(target=injection_worker, daemon=True)
        worker.start()
        
        # Queue multiple texts
        texts = [f"Text {i}" for i in range(10)]
        start_time = time.time()
        
        for text in texts:
            injection_queue.put(text)
        
        # Wait for completion
        injection_queue.join()
        injection_queue.put(None)  # Stop signal
        worker.join()
        
        duration = time.time() - start_time
        
        print(f"\nQueue processing:")
        print(f"  Items: {len(injected_texts)}")
        print(f"  Duration: {duration:.2f}s")
        print(f"  Rate: {len(injected_texts)/duration:.1f} items/sec")
        
        assert injected_texts == texts, "Not all texts were injected correctly"
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_injection_error_recovery(self):
        """Test error recovery during text injection."""
        errors_encountered = []
        successful_injections = []
        
        def inject_with_errors(text: str, error_rate: float = 0.2):
            """Simulate injection with random errors."""
            import random
            
            if random.random() < error_rate:
                error = Exception(f"Injection failed for '{text}'")
                errors_encountered.append(error)
                raise error
            else:
                successful_injections.append(text)
                return True
        
        # Test with retry logic
        texts_to_inject = [f"Message {i}" for i in range(20)]
        max_retries = 3
        
        print("\nTesting injection with errors:")
        for text in texts_to_inject:
            retries = 0
            while retries < max_retries:
                try:
                    inject_with_errors(text, error_rate=0.3)
                    break
                except Exception as e:
                    retries += 1
                    print(f"  Retry {retries} for '{text}'")
                    if retries >= max_retries:
                        print(f"  Failed after {max_retries} retries")
        
        print(f"\nResults:")
        print(f"  Total texts: {len(texts_to_inject)}")
        print(f"  Successful: {len(successful_injections)}")
        print(f"  Errors encountered: {len(errors_encountered)}")
        
        # Should successfully inject most texts despite errors
        success_rate = len(successful_injections) / len(texts_to_inject)
        assert success_rate > 0.8, f"Success rate too low: {success_rate:.1%}"