"""Resource monitoring for hardware tests."""

import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import torch


@dataclass
class ResourceSnapshot:
    """Single point-in-time resource measurement."""

    timestamp: float
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None
    memory_mb: Optional[float] = None
    gpu_memory_mb: Optional[float] = None
    gpu_utilization: Optional[float] = None


class ResourceMonitor:
    """Monitors system resources during test execution."""

    def __init__(self, sample_interval: float = 0.1, max_samples: int = 10000):
        self.sample_interval = sample_interval
        self.max_samples = max_samples
        self.samples: deque[ResourceSnapshot] = deque(maxlen=max_samples)

        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._start_time: float = 0

        # Check what monitoring is available
        self._has_psutil = False
        self._has_gpu = torch.cuda.is_available()

        try:
            import psutil

            self._has_psutil = True
            self._process = psutil.Process()
        except ImportError:
            pass

    def start(self):
        """Start monitoring resources."""
        if self._monitoring:
            return

        self._monitoring = True
        self._start_time = time.time()
        self.samples.clear()

        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop(self):
        """Stop monitoring resources."""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
            self._monitor_thread = None

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._monitoring:
            snapshot = self._take_snapshot()
            self.samples.append(snapshot)
            time.sleep(self.sample_interval)

    def _take_snapshot(self) -> ResourceSnapshot:
        """Take a single resource snapshot."""
        snapshot = ResourceSnapshot(timestamp=time.time())

        # CPU and memory monitoring
        if self._has_psutil:
            try:
                import psutil

                snapshot.cpu_percent = self._process.cpu_percent()

                mem_info = self._process.memory_info()
                snapshot.memory_mb = mem_info.rss / 1024 / 1024
                snapshot.memory_percent = self._process.memory_percent()
            except Exception:
                pass

        # GPU monitoring
        if self._has_gpu:
            try:
                snapshot.gpu_memory_mb = torch.cuda.memory_allocated() / 1024 / 1024

                # Try to get GPU utilization (requires nvidia-ml-py)
                try:
                    import pynvml

                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    snapshot.gpu_utilization = util.gpu
                except Exception:
                    pass

            except Exception:
                pass

        return snapshot

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of resource usage."""
        if not self.samples:
            return {}

        summary = {
            "duration": time.time() - self._start_time,
            "sample_count": len(self.samples),
            "monitoring_available": {
                "cpu": self._has_psutil,
                "memory": self._has_psutil,
                "gpu": self._has_gpu,
            },
        }

        # Calculate statistics for each metric
        metrics = {
            "cpu_percent": [s.cpu_percent for s in self.samples if s.cpu_percent is not None],
            "memory_mb": [s.memory_mb for s in self.samples if s.memory_mb is not None],
            "gpu_memory_mb": [s.gpu_memory_mb for s in self.samples if s.gpu_memory_mb is not None],
            "gpu_utilization": [
                s.gpu_utilization for s in self.samples if s.gpu_utilization is not None
            ],
        }

        for metric_name, values in metrics.items():
            if values:
                summary[metric_name] = {
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "samples": len(values),
                }

        return summary

    def get_peak_usage(self) -> Dict[str, float]:
        """Get peak resource usage."""
        peaks = {}

        if self.samples:
            cpu_values = [s.cpu_percent for s in self.samples if s.cpu_percent is not None]
            if cpu_values:
                peaks["cpu_percent"] = max(cpu_values)

            mem_values = [s.memory_mb for s in self.samples if s.memory_mb is not None]
            if mem_values:
                peaks["memory_mb"] = max(mem_values)

            gpu_mem_values = [s.gpu_memory_mb for s in self.samples if s.gpu_memory_mb is not None]
            if gpu_mem_values:
                peaks["gpu_memory_mb"] = max(gpu_mem_values)

            gpu_util_values = [
                s.gpu_utilization for s in self.samples if s.gpu_utilization is not None
            ]
            if gpu_util_values:
                peaks["gpu_utilization"] = max(gpu_util_values)

        return peaks

    def export_samples(self) -> List[Dict[str, Any]]:
        """Export all samples for detailed analysis."""
        return [
            {
                "timestamp": s.timestamp,
                "cpu_percent": s.cpu_percent,
                "memory_mb": s.memory_mb,
                "gpu_memory_mb": s.gpu_memory_mb,
                "gpu_utilization": s.gpu_utilization,
            }
            for s in self.samples
        ]
