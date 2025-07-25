#!/usr/bin/env python3
"""
Comprehensive Test Runner for PersonalParakeet

This script runs all automated tests that work in WSL/Linux environments,
summarizes their output, and provides analysis of test coverage and issues.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import unittest
import importlib.util

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from personalparakeet.constants import LogEmoji


class TestResult:
    """Container for test execution results"""
    def __init__(self, name: str, description: str, status: str, 
                 output: str = "", error: str = "", execution_time: float = 0.0):
        self.name = name
        self.description = description
        self.status = status  # "PASS", "FAIL", "SKIP", "ERROR"
        self.output = output
        self.error = error
        self.execution_time = execution_time
    
    def __str__(self):
        status_emoji = {
            "PASS": "✅",
            "FAIL": "❌", 
            "SKIP": "⏭️",
            "ERROR": "💥"
        }
        emoji = status_emoji.get(self.status, "❓")
        return f"{emoji} {self.name} ({self.execution_time:.3f}s) - {self.description}"


class TestSuite:
    """Individual test suite configuration"""
    def __init__(self, name: str, description: str, command: List[str], 
                 working_dir: Optional[str] = None, requires_audio: bool = False):
        self.name = name
        self.description = description
        self.command = command
        self.working_dir = working_dir
        self.requires_audio = requires_audio


class ComprehensiveTestRunner:
    """Main test runner that discovers and executes all tests"""
    
    def __init__(self):
        self.test_suites = self._discover_test_suites()
        self.results: List[TestResult] = []
        self.total_start_time = 0.0
        
    def _discover_test_suites(self) -> List[TestSuite]:
        """Discover all available test suites"""
        suites = []
        
        # Unit tests using unittest
        unittest_tests = [
            ("Constants Module", "tests/test_constants.py", 
             "Tests LogEmoji constants and platform detection lists"),
            ("Config Module", "tests/test_config.py", 
             "Tests InjectionConfig dataclass (OUTDATED - missing new fields)"),
            ("Logger Module", "tests/test_logger.py", 
             "Tests logger setup functionality (BROKEN - import issues)")
        ]
        
        for name, path, desc in unittest_tests:
            if Path(path).exists():
                suites.append(TestSuite(
                    name=name,
                    description=desc,
                    command=["python3", "-c", 
                           f"import unittest; import sys; sys.path.append('.'); "
                           f"from {path.replace('/', '.').replace('.py', '')} import *; "
                           f"unittest.main(verbosity=2)"]
                ))
        
        # Standalone test scripts
        standalone_tests = [
            ("LocalAgreement Simulation", "tests/test_local_agreement.py",
             "Simulates LocalAgreement buffering with real transcription scenarios"),
            ("Config System Integration", "test_config_system.py", 
             "Tests complete configuration management system (2 tests fail)"),
            ("Application Detection", "test_application_detection.py",
             "Tests enhanced application detection and profiling system")
        ]
        
        for name, path, desc in standalone_tests:
            if Path(path).exists():
                suites.append(TestSuite(
                    name=name,
                    description=desc,
                    command=["python3", path]
                ))
        
        return suites
    
    def _run_test_suite(self, suite: TestSuite) -> TestResult:
        """Execute a single test suite and capture results"""
        print(f"\n{LogEmoji.PROCESSING} Running {suite.name}...")
        print(f"Description: {suite.description}")
        print(f"Command: {' '.join(suite.command)}")
        print("-" * 60)
        
        start_time = time.time()
        
        try:
            # Check if this test requires audio and we're in WSL
            if suite.requires_audio:
                return TestResult(
                    name=suite.name,
                    description=suite.description,
                    status="SKIP",
                    output="Skipped - requires audio hardware not available in WSL",
                    execution_time=time.time() - start_time
                )
            
            # Execute the test
            result = subprocess.run(
                suite.command,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                cwd=suite.working_dir
            )
            
            execution_time = time.time() - start_time
            
            # Analyze output to determine status
            if result.returncode == 0:
                # Check for specific success indicators
                if ("OK" in result.stdout or 
                    "All tests passed!" in result.stderr or
                    "passed" in result.stderr.lower()):
                    status = "PASS"
                else:
                    status = "PASS"  # Assume pass if return code 0
            else:
                # Check for specific failure indicators  
                if ("FAILED" in result.stdout or "failed" in result.stderr or
                    "Error" in result.stderr or "ImportError" in result.stderr):
                    status = "FAIL"
                else:
                    status = "ERROR"
            
            return TestResult(
                name=suite.name,
                description=suite.description,
                status=status,
                output=result.stdout,
                error=result.stderr,
                execution_time=execution_time
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                name=suite.name,
                description=suite.description,
                status="ERROR",
                error="Test timed out after 2 minutes",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return TestResult(
                name=suite.name,
                description=suite.description,
                status="ERROR", 
                error=f"Failed to execute test: {e}",
                execution_time=time.time() - start_time
            )
    
    def _analyze_missing_coverage(self) -> List[str]:
        """Analyze what modules lack test coverage"""
        personalparakeet_dir = Path("personalparakeet")
        if not personalparakeet_dir.exists():
            return ["personalparakeet directory not found"]
        
        missing_tests = []
        
        # Core modules that should have tests
        critical_modules = [
            ("dictation.py", "Main dictation system - CRITICAL"),
            ("text_injection.py", "Core text injection system - CRITICAL"),
            ("text_injection_enhanced.py", "Enhanced text injection - CRITICAL"),
            ("windows_injection.py", "Windows-specific injection"),
            ("linux_injection.py", "Linux-specific injection"),
            ("kde_injection.py", "KDE-specific injection"),
            ("clipboard_manager.py", "Cross-platform clipboard management"),
            ("config_manager.py", "Configuration management system"),
            ("application_detection.py", "Basic application detection"),
            ("audio_devices.py", "Audio device management"),
            ("dictation_enhanced.py", "Enhanced dictation features")
        ]
        
        for module_name, description in critical_modules:
            module_path = personalparakeet_dir / module_name
            if module_path.exists():
                # Check if corresponding test exists
                test_path = Path(f"tests/test_{module_name}")
                if not test_path.exists():
                    missing_tests.append(f"{module_name} - {description}")
        
        return missing_tests
    
    def _generate_summary_report(self):
        """Generate comprehensive summary report"""
        print(f"\n\n{LogEmoji.INFO} COMPREHENSIVE TEST RESULTS SUMMARY")
        print("=" * 80)
        
        # Overall statistics
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        errors = len([r for r in self.results if r.status == "ERROR"])
        skipped = len([r for r in self.results if r.status == "SKIP"])
        total_time = time.time() - self.total_start_time
        
        print(f"\nOverall Results:")
        print(f"  Total Tests: {total_tests}")
        print(f"  {LogEmoji.SUCCESS} Passed: {passed}")
        print(f"  {LogEmoji.ERROR} Failed: {failed}")
        print(f"  {LogEmoji.ERROR} Errors: {errors}")
        print(f"  ⏭️ Skipped: {skipped}")
        print(f"  Total Time: {total_time:.2f}s")
        
        # Detailed results
        print(f"\nDetailed Results:")
        for result in self.results:
            print(f"  {result}")
            if result.status in ["FAIL", "ERROR"] and result.error:
                # Show first few lines of error
                error_lines = result.error.split('\n')[:3]
                for line in error_lines:
                    if line.strip():
                        print(f"    {LogEmoji.WARNING} {line.strip()}")
        
        # Test coverage analysis
        print(f"\n{LogEmoji.WARNING} Missing Test Coverage:")
        missing_tests = self._analyze_missing_coverage()
        if missing_tests:
            for missing in missing_tests:
                print(f"  - {missing}")
        else:
            print(f"  {LogEmoji.SUCCESS} All critical modules have tests")
        
        # Known issues
        print(f"\n{LogEmoji.ERROR} Known Issues:")
        issues = [
            "test_config.py tests outdated InjectionConfig (missing many new fields)",
            "test_logger.py has import errors (missing get_log_file_path function)", 
            "test_config_system.py has 2 failing tests (file I/O issues)",
            "No tests for core dictation and text injection systems",
            "No tests for Windows/Linux specific injection modules",
            "No tests for clipboard management system"
        ]
        for issue in issues:
            print(f"  - {issue}")
        
        # Recommendations  
        print(f"\n{LogEmoji.INFO} Recommendations:")
        recommendations = [
            "Update test_config.py to test current InjectionConfig with all new fields",
            "Fix test_logger.py import issues",
            "Create tests for core dictation.py module",
            "Create tests for text_injection*.py modules", 
            "Create tests for platform-specific injection modules",
            "Create tests for clipboard management system",
            "Add integration tests for end-to-end functionality"
        ]
        for rec in recommendations:
            print(f"  - {rec}")
        
        # Test quality assessment
        print(f"\n{LogEmoji.TARGET} Test Quality Assessment:")
        print(f"  - Constants tests: {LogEmoji.SUCCESS} Good - tests current implementation")
        print(f"  - Config tests: {LogEmoji.WARNING} Outdated - missing new features")
        print(f"  - LocalAgreement tests: {LogEmoji.SUCCESS} Good - comprehensive simulation")
        print(f"  - Application detection tests: {LogEmoji.SUCCESS} Good - tests current system")
        print(f"  - Overall coverage: {LogEmoji.ERROR} Poor - major modules untested")
    
    def run_all_tests(self):
        """Execute all discovered test suites"""
        print(f"{LogEmoji.INFO} PersonalParakeet Comprehensive Test Runner")
        print(f"Discovered {len(self.test_suites)} test suites")
        print(f"Running on: {sys.platform} (WSL-compatible tests only)")
        
        self.total_start_time = time.time()
        
        # Execute each test suite
        for suite in self.test_suites:
            result = self._run_test_suite(suite)
            self.results.append(result)
        
        # Generate comprehensive report
        self._generate_summary_report()
        
        # Return exit code
        failed_count = len([r for r in self.results if r.status in ["FAIL", "ERROR"]])
        return 0 if failed_count == 0 else 1


def main():
    """Main entry point"""
    runner = ComprehensiveTestRunner()
    return runner.run_all_tests()


if __name__ == "__main__":
    sys.exit(main())