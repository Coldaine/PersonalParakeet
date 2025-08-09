#!/usr/bin/env python3
"""
Performance benchmarking for Wayland Virtual Keyboard Protocol implementation.

This test suite validates the sub-5ms latency requirement for real-time dictation
and provides comprehensive performance metrics.
"""

import time
import logging
import statistics
import pytest
from typing import List, Dict, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

from personalparakeet.core.virtual_keyboard_injector import VirtualKeyboardInjector
from personalparakeet.core.wayland_injector import WaylandInjector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance measurement results."""
    test_name: str
    iterations: int
    min_latency_ms: float
    max_latency_ms: float
    avg_latency_ms: float
    median_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    success_rate: float
    total_chars: int
    chars_per_second: float


class VirtualKeyboardPerformanceTest:
    """Performance testing suite for virtual keyboard implementation."""
    
    def __init__(self):
        self.injector = None
        self.wayland_injector = None
        
    def setup_method(self):
        """Setup for each test method."""
        try:
            self.injector = VirtualKeyboardInjector()
            self.wayland_injector = WaylandInjector()
            logger.info("Performance test setup completed")
        except Exception as e:
            pytest.skip(f"Virtual keyboard not available: {e}")
    
    def teardown_method(self):
        """Cleanup after each test method."""
        if self.injector:
            self.injector.cleanup()
        
    @contextmanager
    def measure_latency(self):
        """Context manager to measure execution latency."""
        start = time.perf_counter()
        yield
        end = time.perf_counter()
        self.last_latency_ms = (end - start) * 1000
    
    def run_performance_test(self, test_func, test_name: str, iterations: int = 100) -> PerformanceMetrics:
        """Run a performance test and collect metrics."""
        latencies = []
        successes = 0
        total_chars = 0
        
        logger.info(f"Running {test_name} performance test ({iterations} iterations)...")
        
        # Warm up
        for _ in range(5):
            try:
                test_func()
            except:
                pass
        
        # Actual test
        start_time = time.perf_counter()
        
        for i in range(iterations):
            try:
                with self.measure_latency():
                    char_count = test_func()
                    
                latencies.append(self.last_latency_ms)
                successes += 1
                total_chars += char_count or 0
                
                # Progress indicator
                if (i + 1) % 10 == 0:
                    logger.debug(f"Completed {i + 1}/{iterations} iterations")
                    
            except Exception as e:
                logger.warning(f"Test iteration {i} failed: {e}")
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        
        if not latencies:
            logger.error(f"No successful iterations for {test_name}")
            return PerformanceMetrics(
                test_name=test_name,
                iterations=iterations,
                min_latency_ms=0,
                max_latency_ms=0,
                avg_latency_ms=0,
                median_latency_ms=0,
                p95_latency_ms=0,
                p99_latency_ms=0,
                success_rate=0,
                total_chars=0,
                chars_per_second=0
            )
        
        # Calculate metrics
        sorted_latencies = sorted(latencies)
        success_rate = successes / iterations
        chars_per_second = total_chars / total_time if total_time > 0 else 0
        
        metrics = PerformanceMetrics(
            test_name=test_name,
            iterations=iterations,
            min_latency_ms=min(latencies),
            max_latency_ms=max(latencies),
            avg_latency_ms=statistics.mean(latencies),
            median_latency_ms=statistics.median(latencies),
            p95_latency_ms=sorted_latencies[int(0.95 * len(sorted_latencies))],
            p99_latency_ms=sorted_latencies[int(0.99 * len(sorted_latencies))],
            success_rate=success_rate,
            total_chars=total_chars,
            chars_per_second=chars_per_second
        )
        
        self.log_metrics(metrics)
        return metrics
    
    def log_metrics(self, metrics: PerformanceMetrics):
        """Log performance metrics in a readable format."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Performance Test Results: {metrics.test_name}")
        logger.info(f"{'='*60}")
        logger.info(f"Iterations:       {metrics.iterations}")
        logger.info(f"Success Rate:     {metrics.success_rate:.1%}")
        logger.info(f"Total Characters: {metrics.total_chars}")
        logger.info(f"Chars/Second:     {metrics.chars_per_second:.1f}")
        logger.info(f"\nLatency Metrics (ms):")
        logger.info(f"  Minimum:        {metrics.min_latency_ms:.3f}")
        logger.info(f"  Maximum:        {metrics.max_latency_ms:.3f}")
        logger.info(f"  Average:        {metrics.avg_latency_ms:.3f}")
        logger.info(f"  Median:         {metrics.median_latency_ms:.3f}")
        logger.info(f"  95th Percentile: {metrics.p95_latency_ms:.3f}")
        logger.info(f"  99th Percentile: {metrics.p99_latency_ms:.3f}")
        
        # Performance assessment
        if metrics.avg_latency_ms < 5.0:
            logger.info(f"✅ PASSED: Average latency {metrics.avg_latency_ms:.3f}ms < 5ms target")
        else:
            logger.warning(f"⚠️ FAILED: Average latency {metrics.avg_latency_ms:.3f}ms > 5ms target")
        
        if metrics.p95_latency_ms < 10.0:
            logger.info(f"✅ PASSED: 95th percentile {metrics.p95_latency_ms:.3f}ms < 10ms acceptable")
        else:
            logger.warning(f"⚠️ CONCERN: 95th percentile {metrics.p95_latency_ms:.3f}ms > 10ms")
    
    def test_single_character_latency(self):
        """Test latency for single character injection."""
        def single_char_test():
            success, error = self.injector.inject_text("a")
            if not success:
                raise Exception(f"Injection failed: {error}")
            return 1
        
        metrics = self.run_performance_test(single_char_test, "Single Character", 200)
        assert metrics.avg_latency_ms < 5.0, f"Single char latency {metrics.avg_latency_ms:.3f}ms > 5ms"
        assert metrics.success_rate > 0.95, f"Success rate {metrics.success_rate:.1%} too low"
    
    def test_short_word_latency(self):
        """Test latency for short word injection."""
        def short_word_test():
            success, error = self.injector.inject_text("hello")
            if not success:
                raise Exception(f"Injection failed: {error}")
            return 5
        
        metrics = self.run_performance_test(short_word_test, "Short Word (5 chars)", 100)
        assert metrics.avg_latency_ms < 10.0, f"Short word latency {metrics.avg_latency_ms:.3f}ms > 10ms"
        assert metrics.success_rate > 0.90, f"Success rate {metrics.success_rate:.1%} too low"
    
    def test_sentence_latency(self):
        """Test latency for sentence injection."""
        test_sentence = "The quick brown fox jumps over the lazy dog."
        
        def sentence_test():
            success, error = self.injector.inject_text(test_sentence)
            if not success:
                raise Exception(f"Injection failed: {error}")
            return len(test_sentence)
        
        metrics = self.run_performance_test(sentence_test, "Full Sentence", 50)
        # Allow higher latency for longer text, but still reasonable
        assert metrics.avg_latency_ms < 50.0, f"Sentence latency {metrics.avg_latency_ms:.3f}ms > 50ms"
        assert metrics.success_rate > 0.85, f"Success rate {metrics.success_rate:.1%} too low"
    
    def test_special_characters_latency(self):
        """Test latency with special characters and modifiers."""
        special_text = "Hello, World! @#$%^&*()"
        
        def special_chars_test():
            success, error = self.injector.inject_text(special_text)
            if not success:
                raise Exception(f"Injection failed: {error}")
            return len(special_text)
        
        metrics = self.run_performance_test(special_chars_test, "Special Characters", 50)
        # Special characters require modifiers, so allow higher latency
        assert metrics.avg_latency_ms < 30.0, f"Special chars latency {metrics.avg_latency_ms:.3f}ms > 30ms"
        assert metrics.success_rate > 0.80, f"Success rate {metrics.success_rate:.1%} too low"
    
    def test_rapid_injection_burst(self):
        """Test rapid successive injections."""
        def burst_test():
            total_chars = 0
            for i in range(10):
                success, error = self.injector.inject_text(f"{i}")
                if not success:
                    raise Exception(f"Injection {i} failed: {error}")
                total_chars += 1
            return total_chars
        
        metrics = self.run_performance_test(burst_test, "Rapid Burst (10 chars)", 20)
        # This tests the overall burst performance, not per-character
        assert metrics.avg_latency_ms < 100.0, f"Burst latency {metrics.avg_latency_ms:.3f}ms > 100ms"
        assert metrics.success_rate > 0.75, f"Success rate {metrics.success_rate:.1%} too low"
    
    def test_wayland_injector_integration(self):
        """Test virtual keyboard through WaylandInjector integration."""
        def integration_test():
            success, error = self.wayland_injector.inject_text("test")
            if not success:
                raise Exception(f"Integration failed: {error}")
            return 4
        
        metrics = self.run_performance_test(integration_test, "WaylandInjector Integration", 50)
        # Should use virtual keyboard as first priority method
        assert metrics.success_rate > 0.80, f"Integration success rate {metrics.success_rate:.1%} too low"
    
    def test_memory_efficiency(self):
        """Test memory usage during sustained operation."""
        import tracemalloc
        
        tracemalloc.start()
        
        # Baseline memory
        baseline_snapshot = tracemalloc.take_snapshot()
        
        # Perform many operations
        for i in range(100):
            success, error = self.injector.inject_text("memory test")
            if not success:
                logger.warning(f"Memory test iteration {i} failed: {error}")
        
        # Final memory
        final_snapshot = tracemalloc.take_snapshot()
        
        # Calculate memory growth
        top_stats = final_snapshot.compare_to(baseline_snapshot, 'lineno')
        total_memory_mb = sum(stat.size_diff for stat in top_stats) / 1024 / 1024
        
        tracemalloc.stop()
        
        logger.info(f"Memory growth after 100 operations: {total_memory_mb:.2f} MB")
        
        # Should not grow significantly during operation
        assert total_memory_mb < 10.0, f"Memory growth {total_memory_mb:.2f}MB too high"
    
    @pytest.mark.performance
    def test_comprehensive_performance_suite(self):
        """Run the complete performance test suite."""
        if not self.injector.is_available():
            pytest.skip("Virtual keyboard not available")
        
        logger.info("Starting comprehensive virtual keyboard performance test suite...")
        
        all_metrics = []
        
        # Run all performance tests
        test_methods = [
            self.test_single_character_latency,
            self.test_short_word_latency,
            self.test_sentence_latency,
            self.test_special_characters_latency,
            self.test_rapid_injection_burst,
            self.test_wayland_injector_integration,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                logger.error(f"Test {test_method.__name__} failed: {e}")
        
        # Memory efficiency test
        try:
            self.test_memory_efficiency()
        except Exception as e:
            logger.error(f"Memory efficiency test failed: {e}")
        
        logger.info("Comprehensive performance test suite completed!")


if __name__ == "__main__":
    # Run performance tests directly
    test_suite = VirtualKeyboardPerformanceTest()
    test_suite.setup_method()
    
    try:
        test_suite.test_comprehensive_performance_suite()
    finally:
        test_suite.teardown_method()