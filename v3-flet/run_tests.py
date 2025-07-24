#!/usr/bin/env python3
"""
Test Runner for PersonalParakeet v3
Runs all automated tests and generates comprehensive report
"""

import sys
import os
import time
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add tests directory to path
sys.path.append(str(Path(__file__).parent / "tests"))

# Import test classes
from test_components import ComponentImportTest
from test_gui_launch import GUILaunchTest
from test_audio_engine import AudioEngineTest
from test_integration import IntegrationTest

async def run_all_tests():
    """Run all automated tests"""
    print("=" * 60)
    print("PersonalParakeet v3 Automated Test Suite")
    print("=" * 60)
    print(f"Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {},
        'overall_status': 'UNKNOWN'
    }
    
    # Test 1: Component Import Test
    print("🔧 Running Component Import Test...")
    import_test = ComponentImportTest()
    import_results = import_test.run_test()
    test_results['tests']['component_imports'] = import_results
    print()
    
    # Test 2: GUI Launch Test (only if imports passed)
    if import_results['overall_result'] == 'PASS':
        print("🚀 Running GUI Launch Test...")
        gui_test = GUILaunchTest()
        gui_results = gui_test.run_test()
        test_results['tests']['gui_launch'] = gui_results
        print()
        
        # Test 3: Audio Engine Test (only if GUI test passed)
        if gui_results['overall_result'] == 'PASS':
            print("🎵 Running Audio Engine Test...")
            audio_test = AudioEngineTest()
            audio_results = await audio_test.run_test()
            test_results['tests']['audio_engine'] = audio_results
            print()
            
            # Test 4: Integration Test (only if audio test passed)
            if audio_results['overall_result'] == 'PASS':
                print("🔗 Running Integration Test...")
                integration_test = IntegrationTest()
                integration_results = await integration_test.run_test()
                test_results['tests']['integration'] = integration_results
            else:
                print("⚠️  Skipping Integration Test (audio engine test failed)")
                test_results['tests']['integration'] = {
                    'overall_result': 'SKIPPED',
                    'reason': 'Audio engine test failed'
                }
        else:
            print("⚠️  Skipping Audio Engine Test (GUI test failed)")
            test_results['tests']['audio_engine'] = {
                'overall_result': 'SKIPPED',
                'reason': 'GUI test failed'
            }
            test_results['tests']['integration'] = {
                'overall_result': 'SKIPPED',
                'reason': 'GUI test failed'
            }
    else:
        print("⚠️  Skipping GUI Launch Test (import failures detected)")
        test_results['tests']['gui_launch'] = {
            'overall_result': 'SKIPPED',
            'reason': 'Import test failed'
        }
        test_results['tests']['audio_engine'] = {
            'overall_result': 'SKIPPED',
            'reason': 'Import test failed'
        }
        test_results['tests']['integration'] = {
            'overall_result': 'SKIPPED',
            'reason': 'Import test failed'
        }
    
    # Generate overall assessment
    print("\n" + "=" * 60)
    print("OVERALL TEST RESULTS")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in test_results['tests'].items():
        status = result.get('overall_result', 'UNKNOWN')
        print(f"{test_name}: {status}")
        if status not in ['PASS', 'SKIPPED']:
            all_passed = False
    
    test_results['overall_status'] = 'PASS' if all_passed else 'FAIL'
    
    # Critical assessment
    print("\n" + "-" * 40)
    if test_results['overall_status'] == 'PASS':
        print("🎉 ALL TESTS PASSED")
        print("✓ Components can be imported without errors")
        if test_results['tests']['gui_launch']['overall_result'] == 'PASS':
            print("✓ GUI launches successfully without user interaction")
            print("✓ Application starts and initializes core components")
        print("\nStatus: Code appears to be functional (based on automated tests)")
    else:
        print("❌ TESTS FAILED")
        print("\nCritical Issues Detected:")
        
        # Analyze failures
        if test_results['tests']['component_imports']['overall_result'] != 'PASS':
            print("- Import errors prevent application startup")
            print("- Code cannot be executed due to missing dependencies or syntax errors")
        
        if test_results['tests'].get('gui_launch', {}).get('overall_result') == 'FAIL':
            print("- GUI fails to launch properly")
            print("- Application may crash or hang during startup")
        
        print("\nStatus: Code has significant issues requiring fixes")
    
    # Save detailed results
    results_file = Path(__file__).parent / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nDetailed results saved to: {results_file}")
    print(f"Test run completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return test_results['overall_status'] == 'PASS'

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)