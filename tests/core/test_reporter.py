"""Test result reporting utilities."""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class TestReporter:
    """Collects and reports test results."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("test_reports")
        self.output_dir.mkdir(exist_ok=True)
        
        self.session_start = time.time()
        self.test_results: List[Dict[str, Any]] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_test_result(self, result: Dict[str, Any]):
        """Add a test result to the report."""
        self.test_results.append(result)
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate test session summary."""
        summary = {
            "session_id": self.session_id,
            "start_time": self.session_start,
            "end_time": time.time(),
            "duration": time.time() - self.session_start,
            "total_tests": len(self.test_results),
            "hardware_tests": 0,
            "resource_summary": {},
            "performance_metrics": {}
        }
        
        # Count test types
        for result in self.test_results:
            if "hardware" in result.get("test_name", ""):
                summary["hardware_tests"] += 1
        
        # Aggregate resource usage
        cpu_max = []
        memory_max = []
        gpu_memory_max = []
        
        for result in self.test_results:
            if result.get("resource_usage"):
                usage = result["resource_usage"]
                if "cpu_percent" in usage and "max" in usage["cpu_percent"]:
                    cpu_max.append(usage["cpu_percent"]["max"])
                if "memory_mb" in usage and "max" in usage["memory_mb"]:
                    memory_max.append(usage["memory_mb"]["max"])
                if "gpu_memory_mb" in usage and "max" in usage["gpu_memory_mb"]:
                    gpu_memory_max.append(usage["gpu_memory_mb"]["max"])
        
        if cpu_max:
            summary["resource_summary"]["peak_cpu_percent"] = max(cpu_max)
        if memory_max:
            summary["resource_summary"]["peak_memory_mb"] = max(memory_max)
        if gpu_memory_max:
            summary["resource_summary"]["peak_gpu_memory_mb"] = max(gpu_memory_max)
        
        # Test performance metrics
        test_durations = [r["duration"] for r in self.test_results if "duration" in r]
        if test_durations:
            summary["performance_metrics"] = {
                "min_duration": min(test_durations),
                "max_duration": max(test_durations),
                "avg_duration": sum(test_durations) / len(test_durations),
                "total_duration": sum(test_durations)
            }
        
        # Save summary
        self._save_report(summary)
        
        return summary
    
    def _save_report(self, summary: Dict[str, Any]):
        """Save test report to file."""
        report_file = self.output_dir / f"test_report_{self.session_id}.json"
        
        report = {
            "summary": summary,
            "test_results": self.test_results
        }
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Also save a human-readable report
        self._save_readable_report(summary)
    
    def _save_readable_report(self, summary: Dict[str, Any]):
        """Save human-readable test report."""
        report_file = self.output_dir / f"test_report_{self.session_id}.txt"
        
        lines = [
            "PersonalParakeet Hardware Test Report",
            "=" * 50,
            f"Session ID: {summary['session_id']}",
            f"Duration: {summary['duration']:.2f} seconds",
            f"Total Tests: {summary['total_tests']}",
            "",
            "Resource Usage:",
            "-" * 30
        ]
        
        if summary["resource_summary"]:
            for key, value in summary["resource_summary"].items():
                lines.append(f"  {key}: {value:.2f}")
        else:
            lines.append("  No resource data collected")
        
        lines.extend([
            "",
            "Performance Metrics:",
            "-" * 30
        ])
        
        if summary["performance_metrics"]:
            metrics = summary["performance_metrics"]
            lines.extend([
                f"  Min Duration: {metrics['min_duration']:.3f}s",
                f"  Max Duration: {metrics['max_duration']:.3f}s",
                f"  Avg Duration: {metrics['avg_duration']:.3f}s",
                f"  Total Time: {metrics['total_duration']:.3f}s"
            ])
        else:
            lines.append("  No performance data collected")
        
        lines.extend([
            "",
            "Test Results:",
            "-" * 30
        ])
        
        for result in self.test_results:
            lines.append(f"\n  {result['test_name']}:")
            lines.append(f"    Duration: {result.get('duration', 0):.3f}s")
            
            if result.get("resource_usage"):
                usage = result["resource_usage"]
                if "cpu_percent" in usage:
                    lines.append(f"    CPU: {usage['cpu_percent'].get('avg', 0):.1f}% avg, {usage['cpu_percent'].get('max', 0):.1f}% max")
                if "memory_mb" in usage:
                    lines.append(f"    Memory: {usage['memory_mb'].get('avg', 0):.1f}MB avg, {usage['memory_mb'].get('max', 0):.1f}MB max")
                if "gpu_memory_mb" in usage:
                    lines.append(f"    GPU Memory: {usage['gpu_memory_mb'].get('avg', 0):.1f}MB avg, {usage['gpu_memory_mb'].get('max', 0):.1f}MB max")
        
        with open(report_file, "w") as f:
            f.write("\n".join(lines))
    
    def print_summary(self):
        """Print test summary to console."""
        summary = self.generate_summary()
        
        print("\n" + "=" * 50)
        print("Test Session Summary")
        print("=" * 50)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Duration: {summary['duration']:.2f}s")
        
        if summary["resource_summary"]:
            print("\nPeak Resource Usage:")
            for key, value in summary["resource_summary"].items():
                print(f"  {key}: {value:.2f}")
        
        print("\nReport saved to:", self.output_dir / f"test_report_{self.session_id}.txt")