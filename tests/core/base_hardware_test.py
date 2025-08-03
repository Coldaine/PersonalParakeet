"""Base class for all hardware tests."""

import asyncio
import time
from abc import ABC
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
import torch

from .hardware_validator import HardwareValidator
from .resource_monitor import ResourceMonitor
from .test_reporter import TestReporter


class BaseHardwareTest(ABC):
    """Base class for all hardware tests.
    
    Provides common setup/teardown, resource monitoring, and reporting.
    """
    
    hardware_validator: Optional[HardwareValidator] = None
    resource_monitor: Optional[ResourceMonitor] = None
    test_reporter: Optional[TestReporter] = None
    
    _audio_device = None
    _gpu_available = False
    _test_start_time: float = 0
    _test_results: Dict[str, Any] = {}
    
    @classmethod
    def setup_class(cls):
        """Initialize hardware resources for test class."""
        cls.hardware_validator = HardwareValidator()
        cls.test_reporter = TestReporter()
        
        # Validate hardware availability
        validation_results = cls.hardware_validator.validate_all()
        if not validation_results["audio"]["available"]:
            pytest.skip("No audio devices available")
        
        cls._gpu_available = validation_results["gpu"]["available"]
        if not cls._gpu_available:
            print("WARNING: GPU not available, tests may run slower")
        
        # Initialize audio if available
        cls._audio_device = validation_results["audio"].get("default_device")
        
    @classmethod
    def teardown_class(cls):
        """Clean up hardware resources."""
        if cls.test_reporter:
            cls.test_reporter.generate_summary()
        
        # Clean up CUDA cache if GPU was used
        if cls._gpu_available and torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    def setup_method(self, method):
        """Per-test setup."""
        self._test_start_time = time.time()
        self._test_results = {
            "test_name": method.__name__,
            "start_time": self._test_start_time,
            "hardware_state": self.hardware_validator.get_current_state()
        }
        
        # Start resource monitoring
        self.resource_monitor = ResourceMonitor()
        self.resource_monitor.start()
    
    def teardown_method(self, method):
        """Per-test cleanup."""
        if self.resource_monitor:
            self.resource_monitor.stop()
            
        # Collect test results
        self._test_results.update({
            "duration": time.time() - self._test_start_time,
            "resource_usage": self.resource_monitor.get_summary() if self.resource_monitor else None,
            "end_time": time.time()
        })
        
        # Report results
        if self.test_reporter:
            self.test_reporter.add_test_result(self._test_results)
    
    @property
    def audio_device(self):
        """Get the default audio device for testing."""
        return self._audio_device
    
    @property
    def gpu_available(self):
        """Check if GPU is available for testing."""
        return self._gpu_available
    
    def assert_hardware_available(self, hardware_type: str):
        """Assert that specific hardware is available."""
        if hardware_type == "gpu" and not self._gpu_available:
            pytest.skip(f"{hardware_type} not available")
        elif hardware_type == "audio" and not self._audio_device:
            pytest.skip(f"{hardware_type} not available")
    
    async def run_async_test(self, coro):
        """Helper to run async tests."""
        return await asyncio.get_event_loop().run_in_executor(None, asyncio.run, coro)
    
    def get_test_fixture_path(self, filename: str) -> Path:
        """Get path to test fixture file."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / filename
        if not fixture_path.exists():
            raise FileNotFoundError(f"Test fixture not found: {fixture_path}")
        return fixture_path
    
    def skip_if_slow_hardware(self, min_gpu_memory_gb: float = 4.0):
        """Skip test if hardware doesn't meet minimum requirements."""
        if self._gpu_available:
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            if gpu_memory < min_gpu_memory_gb:
                pytest.skip(f"Insufficient GPU memory: {gpu_memory:.1f}GB < {min_gpu_memory_gb}GB")