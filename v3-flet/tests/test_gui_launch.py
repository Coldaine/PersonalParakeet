#!/usr/bin/env python3
"""
Automated GUI Launch Test for PersonalParakeet v3
Tests that the application launches without errors and displays the GUI
"""

import sys
import os
import time
import threading
import logging
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Setup logging to capture all output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('test_gui_launch.log')
    ]
)
logger = logging.getLogger(__name__)

class GUILaunchTest:
    """Test class for verifying GUI launch"""
    
    def __init__(self):
        self.app_process = None
        self.test_results = {
            'process_started': False,
            'no_import_errors': False,
            'flet_app_initialized': False,
            'parakeet_model_loading': False,
            'window_creation': False,
            'error_count': 0,
            'runtime_seconds': 0
        }
        self.start_time = None
        
    def start_app_process(self):
        """Start the PersonalParakeet v3 application in a subprocess"""
        try:
            logger.info("Starting PersonalParakeet v3 application...")
            
            # Change to the v3-flet directory
            app_dir = Path(__file__).parent.parent
            
            self.app_process = subprocess.Popen(
                [sys.executable, 'main.py'],
                cwd=app_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.test_results['process_started'] = True
            self.start_time = time.time()
            logger.info("✓ Process started successfully")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to start process: {e}")
            return False
    
    def monitor_app_output(self, timeout_seconds=30):
        """Monitor application output for success indicators"""
        logger.info(f"Monitoring application output for {timeout_seconds} seconds...")
        
        start_time = time.time()
        output_lines = []
        
        while time.time() - start_time < timeout_seconds:
            if self.app_process.poll() is not None:
                # Process ended
                break
                
            try:
                line = self.app_process.stdout.readline()
                if line:
                    line = line.strip()
                    output_lines.append(line)
                    logger.info(f"APP: {line}")
                    
                    # Check for success indicators
                    if "import" in line.lower() and "error" in line.lower():
                        self.test_results['error_count'] += 1
                        logger.error("✗ Import error detected")
                    elif "Starting PersonalParakeet v3 Flet Application" in line:
                        self.test_results['flet_app_initialized'] = True
                        logger.info("✓ Flet application initialized")
                    elif "Loading Parakeet-TDT-1.1B model" in line:
                        self.test_results['parakeet_model_loading'] = True
                        logger.info("✓ Parakeet model loading started")
                    elif "Window configured for floating transparent UI" in line:
                        self.test_results['window_creation'] = True
                        logger.info("✓ Window configuration completed")
                    elif "PersonalParakeet v3 is ready" in line:
                        logger.info("✓ Application reports ready status")
                    elif "error" in line.lower() or "exception" in line.lower():
                        self.test_results['error_count'] += 1
                        logger.warning(f"⚠ Potential error: {line}")
                        
            except Exception as e:
                logger.error(f"Error reading output: {e}")
                break
        
        # If we made it through imports without import errors, mark as success
        if self.test_results['error_count'] == 0 and len(output_lines) > 0:
            self.test_results['no_import_errors'] = True
            
        self.test_results['runtime_seconds'] = time.time() - self.start_time
        
        return output_lines
    
    def terminate_app(self):
        """Terminate the application process"""
        if self.app_process:
            try:
                logger.info("Terminating application...")
                self.app_process.terminate()
                
                # Wait up to 5 seconds for graceful shutdown
                try:
                    self.app_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Forcing application termination...")
                    self.app_process.kill()
                    
                logger.info("✓ Application terminated")
            except Exception as e:
                logger.error(f"Error terminating app: {e}")
    
    def run_test(self):
        """Run the complete GUI launch test"""
        logger.info("=== PersonalParakeet v3 GUI Launch Test ===")
        
        try:
            # Start the application
            if not self.start_app_process():
                return self.generate_report()
            
            # Monitor for success indicators
            output_lines = self.monitor_app_output(timeout_seconds=45)
            
            # Terminate the application
            self.terminate_app()
            
            return self.generate_report()
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        logger.info("=== TEST RESULTS ===")
        
        passed_tests = []
        failed_tests = []
        
        for test_name, result in self.test_results.items():
            if test_name in ['error_count', 'runtime_seconds']:
                continue
                
            if result:
                passed_tests.append(test_name)
                logger.info(f"✓ {test_name}: PASS")
            else:
                failed_tests.append(test_name)
                logger.error(f"✗ {test_name}: FAIL")
        
        # Summary statistics
        logger.info(f"Runtime: {self.test_results['runtime_seconds']:.1f} seconds")
        logger.info(f"Errors detected: {self.test_results['error_count']}")
        logger.info(f"Tests passed: {len(passed_tests)}/{len(passed_tests) + len(failed_tests)}")
        
        # Overall assessment
        critical_tests = ['process_started', 'no_import_errors', 'flet_app_initialized']
        critical_passed = all(self.test_results[test] for test in critical_tests)
        
        if critical_passed and self.test_results['error_count'] == 0:
            logger.info("🎉 OVERALL: GUI LAUNCH TEST PASSED")
            overall_result = "PASS"
        else:
            logger.error("❌ OVERALL: GUI LAUNCH TEST FAILED")
            overall_result = "FAIL"
        
        # Return structured results
        return {
            'overall_result': overall_result,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'error_count': self.test_results['error_count'],
            'runtime_seconds': self.test_results['runtime_seconds'],
            'critical_tests_passed': critical_passed
        }


if __name__ == "__main__":
    # Run the GUI launch test
    test = GUILaunchTest()
    results = test.run_test()
    
    # Exit with appropriate code
    exit_code = 0 if results['overall_result'] == 'PASS' else 1
    sys.exit(exit_code)