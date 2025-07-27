#!/usr/bin/env python3
"""
Surgical Test Audit: Runtime & Flakiness Profiler
Measures test execution performance and identifies flaky tests
"""

import time
import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import statistics
from dataclasses import dataclass, asdict
import tempfile
import threading
import concurrent.futures
from datetime import datetime

@dataclass
class TestExecution:
    """Single test execution result"""
    test_name: str
    test_file: str
    duration: float
    success: bool
    output: str
    error: Optional[str]
    timestamp: str

@dataclass
class TestProfile:
    """Complete profile for a test across multiple runs"""
    test_name: str
    test_file: str
    avg_duration: float
    min_duration: float
    max_duration: float
    std_dev: float
    success_rate: float
    flakiness_score: float
    total_runs: int
    recent_failures: List[str]
    performance_trend: str  # 'stable', 'degrading', 'improving'

class TestRuntimeProfiler:
    """Profiles test execution performance and flakiness"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.profiles = {}
        
    def discover_test_methods(self, test_file: Path) -> List[str]:
        """Discover all test methods in a test file"""
        try:
            content = test_file.read_text()
            import ast
            
            tree = ast.parse(content)
            test_methods = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_name = node.name
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            if item.name.startswith('test_'):
                                test_methods.append(f"{class_name}.{item.name}")
                                
                elif isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        test_methods.append(node.name)
                        
            return test_methods
        except Exception as e:
            print(f"Error parsing {test_file}: {e}")
            return []
    
    def run_single_test(self, test_file: Path, test_method: str, timeout: int = 30) -> TestExecution:
        """Run a single test method and capture results"""
        start_time = time.time()
        
        try:
            # Build pytest command
            cmd = [
                sys.executable, '-m', 'pytest',
                str(test_file),
                '-v',
                '-k', test_method,
                '--tb=short'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            return TestExecution(
                test_name=test_method,
                test_file=str(test_file),
                duration=duration,
                success=success,
                output=result.stdout,
                error=result.stderr if not success else None,
                timestamp=datetime.now().isoformat()
            )
            
        except subprocess.TimeoutExpired:
            return TestExecution(
                test_name=test_method,
                test_file=str(test_file),
                duration=timeout,
                success=False,
                output="",
                error="Test timed out",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return TestExecution(
                test_name=test_method,
                test_file=str(test_file),
                duration=time.time() - start_time,
                success=False,
                output="",
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    def profile_test_runs(self, test_file: Path, test_method: str, runs: int = 5) -> TestProfile:
        """Profile a test across multiple runs to detect flakiness"""
        executions = []
        
        print(f"  Profiling {test_method} ({runs} runs)...")
        
        # Run test multiple times
        for i in range(runs):
            execution = self.run_single_test(test_file, test_method)
            executions.append(execution)
            
            # Small delay between runs
            time.sleep(0.1)
        
        # Calculate statistics
        durations = [e.duration for e in executions]
        successes = [e.success for e in executions]
        
        avg_duration = statistics.mean(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        std_dev = statistics.stdev(durations) if len(durations) > 1 else 0
        
        success_rate = sum(successes) / len(successes)
        
        # Calculate flakiness score (0-1, higher = more flaky)
        flakiness_score = 1.0 - success_rate
        
        # Determine performance trend
        if std_dev / avg_duration > 0.5:  # High variability
            performance_trend = 'unstable'
        elif max_duration > avg_duration * 2:
            performance_trend = 'degrading'
        elif std_dev / avg_duration < 0.1:
            performance_trend = 'stable'
        else:
            performance_trend = 'stable'
        
        # Collect recent failures
        recent_failures = [
            e.error for e in executions[-3:] 
            if not e.success and e.error
        ]
        
        return TestProfile(
            test_name=test_method,
            test_file=str(test_file),
            avg_duration=avg_duration,
            min_duration=min_duration,
            max_duration=max_duration,
            std_dev=std_dev,
            success_rate=success_rate,
            flakiness_score=flakiness_score,
            total_runs=runs,
            recent_failures=recent_failures,
            performance_trend=performance_trend
        )
    
    def profile_all_tests(self, test_files: List[Path], runs_per_test: int = 3) -> Dict[str, TestProfile]:
        """Profile all tests in the project"""
        profiles = {}
        
        print(f"🔍 Profiling {len(test_files)} test files...")
        
        for test_file in test_files:
            print(f"\n📁 {test_file.name}:")
            
            test_methods = self.discover_test_methods(test_file)
            
            for test_method in test_methods:
                profile = self.profile_test_runs(test_file, test_method, runs_per_test)
                key = f"{test_file}:{test_method}"
                profiles[key] = profile
                
                # Print summary
                status = "✅" if profile.success_rate == 1.0 else "❌"
                print(f"  {status} {test_method}: {profile.avg_duration:.2f}s ±{profile.std_dev:.2f}s "
                      f"(flakiness: {profile.flakiness_score:.2f})")
        
        return profiles
    
    def identify_performance_bottlenecks(self, profiles: Dict[str, TestProfile]) -> List[Dict]:
        """Identify slow and flaky tests that need optimization"""
        bottlenecks = []
        
        for key, profile in profiles.items():
            issues = []
            
            # Check for slow tests
            if profile.avg_duration > 5.0:
                issues.append(f"Slow ({profile.avg_duration:.1f}s)")
                
            # Check for flaky tests
            if profile.flakiness_score > 0.2:
                issues.append(f"Flaky ({profile.flakiness_score:.1f})")
                
            # Check for unstable performance
            if profile.performance_trend == 'unstable':
                issues.append("Unstable performance")
                
            if issues:
                bottlenecks.append({
                    'test': key,
                    'issues': issues,
                    'avg_duration': profile.avg_duration,
                    'flakiness_score': profile.flakiness_score,
                    'priority': len(issues)  # More issues = higher priority
                })
        
        return sorted(bottlenecks, key=lambda x: x['priority'], reverse=True)
    
    def generate_runtime_report(self, profiles: Dict[str, TestProfile]) -> Dict:
        """Generate comprehensive runtime analysis report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(profiles),
            'summary': {
                'total_execution_time': sum(p.avg_duration for p in profiles.values()),
                'average_test_time': statistics.mean([p.avg_duration for p in profiles.values()]),
                'median_test_time': statistics.median([p.avg_duration for p in profiles.values()]),
                'flaky_tests': sum(1 for p in profiles.values() if p.flakiness_score > 0.1),
                'slow_tests': sum(1 for p in profiles.values() if p.avg_duration > 5.0)
            },
            'profiles': {k: asdict(v) for k, v in profiles.items()},
            'bottlenecks': self.identify_performance_bottlenecks(profiles),
            'recommendations': []
        }
        
        # Generate recommendations
        if report['summary']['flaky_tests'] > 0:
            report['recommendations'].append({
                'type': 'flakiness',
                'message': f"Found {report['summary']['flaky_tests']} flaky tests that need attention",
                'priority': 'high'
            })
            
        if report['summary']['slow_tests'] > 0:
            report['recommendations'].append({
                'type': 'performance',
                'message': f"Found {report['summary']['slow_tests']} slow tests (>5s) that could be optimized",
                'priority': 'medium'
            })
            
        if report['summary']['total_execution_time'] > 60:
            report['recommendations'].append({
                'type': 'parallelization',
                'message': "Consider parallel test execution to reduce total runtime",
                'priority': 'low'
            })
        
        return report
    
    def run_runtime_audit(self, test_files: List[Path]) -> Dict:
        """Execute complete runtime and flakiness audit"""
        print("🚀 Starting runtime and flakiness audit...")
        
        # Profile all tests
        profiles = self.profile_all_tests(test_files, runs_per_test=3)
        
        # Generate report
        report = self.generate_runtime_report(profiles)
        
        # Save report
        report_file = self.project_root / 'runtime_audit_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)
        
        print(f"\n✅ Runtime audit complete! Report saved to {report_file}")
        
        # Print summary
        print(f"\n📊 Runtime Summary:")
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Total Runtime: {report['summary']['total_execution_time']:.1f}s")
        print(f"Average Test: {report['summary']['average_test_time']:.2f}s")
        print(f"Flaky Tests: {report['summary']['flaky_tests']}")
        print(f"Slow Tests: {report['summary']['slow_tests']}")
        
        if report['bottlenecks']:
            print(f"\n⚠️  Performance Issues:")
            for bottleneck in report['bottlenecks'][:3]:
                print(f"  {bottleneck['test']}: {', '.join(bottleneck['issues'])}")
        
        return report

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    profiler = TestRuntimeProfiler(project_root)
    
    # Discover test files
    test_patterns = ['test_*.py', '*_test.py']
    test_files = []
    
    for pattern in test_patterns:
        test_files.extend(project_root.rglob(pattern))
    
    # Filter to relevant directories
    relevant_dirs = ['v3-flet/tests', 'v2_legacy_archive/tests']
    filtered = []
    
    for test_file in test_files:
        for dir_name in relevant_dirs:
            if dir_name in str(test_file):
                filtered.append(test_file)
                break
    
    # Run runtime audit
    report = profiler.run_runtime_audit(filtered)