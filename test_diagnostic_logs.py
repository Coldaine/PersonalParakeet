#!/usr/bin/env python3
"""
Diagnostic script to validate assumptions about test infrastructure and GPU resource management issues.
This script adds detailed logging to help identify the root causes of problems found in test reports.
"""

import os
import sys
import logging
import time
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diagnostic_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_discovery_diagnostics():
    """Test 1: Diagnose test discovery and execution infrastructure issues"""
    logger.info("=== TEST DISCOVERY DIAGNOSTICS ===")
    
    # Check test file locations
    test_dirs = [
        "tests/",
        "src/personalparakeet/tests/",
        "tests/integration/",
        "tests/unit/",
        "tests/hardware/"
    ]
    
    for test_dir in test_dirs:
        dir_path = Path(test_dir)
        if dir_path.exists():
            test_files = list(dir_path.glob("test_*.py"))
            logger.info(f"Found {len(test_files)} test files in {test_dir}")
            for test_file in test_files:
                logger.debug(f"  - {test_file}")
        else:
            logger.warning(f"Test directory not found: {test_dir}")
    
    # Check pytest configuration
    logger.info("Checking pytest configuration...")
    
    # Test if pytest can discover tests
    try:
        import pytest
        logger.info("Pytest is available")
        
        # Try to collect tests from main test directory
        test_collection_start = time.time()
        args = ["--collect-only", "tests/"]
        try:
            collected = pytest.main(args)
            collection_time = time.time() - test_collection_start
            logger.info(f"Test collection completed in {collection_time:.2f} seconds")
            logger.info(f"Pytest collection result: {collected}")
        except Exception as e:
            logger.error(f"Test collection failed: {e}")
            
    except ImportError:
        logger.error("Pytest not available")
    
    # Check environment variables that might affect test execution
    test_env_vars = [
        'CI', 'GITHUB_ACTIONS', 'PARAKEET_TEST_MODE', 
        'PARAKEET_MOCK_AUDIO', 'PARAKEET_DISABLE_GUI'
    ]
    
    logger.info("Environment variables affecting tests:")
    for var in test_env_vars:
        value = os.getenv(var)
        if value:
            logger.info(f"  {var} = {value}")
        else:
            logger.debug(f"  {var} = (not set)")

def gpu_resource_diagnostics():
    """Test 2: Diagnose GPU resource management and CPU spike issues"""
    logger.info("=== GPU RESOURCE DIAGNOSTICS ===")
    
    # Check CUDA availability
    try:
        import torch
        logger.info(f"PyTorch version: {torch.__version__}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            logger.info(f"CUDA version: {torch.version.cuda}")
            logger.info(f"GPU device count: {torch.cuda.device_count()}")
            logger.info(f"Current GPU device: {torch.cuda.current_device()}")
            logger.info(f"GPU device name: {torch.cuda.get_device_name(0)}")
            
            # Check GPU memory
            props = torch.cuda.get_device_properties(0)
            total_memory = props.total_memory / (1024**3)  # Convert to GB
            logger.info(f"Total GPU memory: {total_memory:.2f} GB")
            
            # Check current memory usage
            allocated = torch.cuda.memory_allocated() / (1024**3)
            reserved = torch.cuda.memory_reserved() / (1024**3)
            logger.info(f"Currently allocated GPU memory: {allocated:.3f} GB")
            logger.info(f"Currently reserved GPU memory: {reserved:.3f} GB")
            
            # Test basic GPU operations and monitor CPU usage
            logger.info("Testing basic GPU operations...")
            
            # Test 1: Simple tensor creation
            start_time = time.time()
            start_cpu_load = get_cpu_load()
            
            test_tensor = torch.randn(1000, 1000).cuda()
            torch.cuda.synchronize()
            
            end_time = time.time()
            end_cpu_load = get_cpu_load()
            
            logger.info(f"Simple tensor creation: {end_time - start_time:.3f}s")
            logger.info(f"CPU load during operation: {start_cpu_load:.1f}% -> {end_cpu_load:.1f}%")
            
            # Clean up
            del test_tensor
            torch.cuda.empty_cache()
            
            # Test 2: More complex operation (matrix multiplication)
            start_time = time.time()
            start_cpu_load = get_cpu_load()
            
            a = torch.randn(2000, 2000).cuda()
            b = torch.randn(2000, 2000).cuda()
            c = torch.matmul(a, b)
            torch.cuda.synchronize()
            
            end_time = time.time()
            end_cpu_load = get_cpu_load()
            
            logger.info(f"Matrix multiplication: {end_time - start_time:.3f}s")
            logger.info(f"CPU load during operation: {start_cpu_load:.1f}% -> {end_cpu_load:.1f}%")
            
            # Clean up
            del a, b, c
            torch.cuda.empty_cache()
            
        else:
            logger.warning("CUDA not available - running on CPU")
            
    except ImportError:
        logger.error("PyTorch not available")

def get_cpu_load():
    """Get current CPU load percentage"""
    try:
        import psutil
        return psutil.cpu_percent(interval=0.1)
    except ImportError:
        logger.warning("psutil not available for CPU monitoring")
        return 0.0

def test_configuration_diagnostics():
    """Test 3: Diagnose configuration and dependency issues"""
    logger.info("=== CONFIGURATION DIAGNOSTICS ===")
    
    # Check key dependencies
    dependencies = [
        'torch', 'numpy', 'pytest', 'sounddevice', 
        'soundfile', 'keyboard', 'pynput', 'pyperclip'
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            logger.info(f"✓ {dep} is available")
        except ImportError:
            logger.warning(f"✗ {dep} is not available")
    
    # Check if we can import the main application modules
    app_modules = [
        'personalparakeet.config',
        'personalparakeet.core.stt_processor',
        'personalparakeet.core.cuda_compatibility',
        'personalparakeet.core.stt_factory'
    ]
    
    for module in app_modules:
        try:
            __import__(module)
            logger.info(f"✓ {module} imports successfully")
        except ImportError as e:
            logger.error(f"✗ {module} import failed: {e}")
        except Exception as e:
            logger.warning(f"? {module} import warning: {e}")

def analyze_test_reports():
    """Test 4: Analyze existing test reports for patterns"""
    logger.info("=== TEST REPORT ANALYSIS ===")
    
    test_report_dir = Path("test_reports")
    if not test_report_dir.exists():
        logger.warning("No test_reports directory found")
        return
    
    # Analyze recent test reports
    report_files = sorted(test_report_dir.glob("test_report_*.json"), reverse=True)[:10]
    
    successful_runs = 0
    failed_runs = 0
    total_tests = 0
    empty_runs = 0
    
    for report_file in report_files:
        try:
            with open(report_file, 'r') as f:
                report = json.load(f)
            
            summary = report.get('summary', {})
            test_count = summary.get('total_tests', 0)
            
            if test_count == 0:
                empty_runs += 1
                logger.warning(f"Empty test run: {report_file.name}")
            else:
                successful_runs += 1
                total_tests += test_count
                
            logger.debug(f"Report {report_file.name}: {test_count} tests")
            
        except Exception as e:
            logger.error(f"Failed to read report {report_file}: {e}")
            failed_runs += 1
    
    logger.info(f"Test report analysis:")
    logger.info(f"  Successful runs: {successful_runs}")
    logger.info(f"  Failed runs: {failed_runs}")
    logger.info(f"  Empty runs: {empty_runs}")
    logger.info(f"  Total tests across all runs: {total_tests}")

def main():
    """Run all diagnostic tests"""
    logger.info("Starting comprehensive diagnostic analysis")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    try:
        test_discovery_diagnostics()
        gpu_resource_diagnostics()
        test_configuration_diagnostics()
        analyze_test_reports()
        
        logger.info("=== DIAGNOSTIC COMPLETE ===")
        logger.info("Check diagnostic_analysis.log for detailed results")
        
    except Exception as e:
        logger.error(f"Diagnostic failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()