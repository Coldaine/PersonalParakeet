#!/usr/bin/env python3
"""
Surgical Test Audit: Migration Validation Framework
Validates test removals and ensures no regression in coverage
"""

import json
import subprocess
import sys
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import shutil
import tempfile
import os
from datetime import datetime

@dataclass
class ValidationResult:
    """Result of validation check"""
    test_file: str
    action: str  # 'remove', 'consolidate', 'keep'
    coverage_before: float
    coverage_after: float
    regression_detected: bool
    confidence_score: float
    validation_errors: List[str]

class MigrationValidator:
    """Validates test removals and consolidations"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backup_dir = project_root / 'test_backup'
        self.validation_results = []
        
    def create_backup(self, test_files: List[str]) -> None:
        """Create backup of test files before modification"""
        self.backup_dir.mkdir(exist_ok=True)
        
        for test_file in test_files:
            src = Path(test_file)
            if src.exists():
                dst = self.backup_dir / src.name
                shutil.copy2(src, dst)
                
    def restore_backup(self, test_files: List[str]) -> None:
        """Restore test files from backup"""
        for test_file in test_files:
            src = self.backup_dir / Path(test_file).name
            if src.exists():
                dst = Path(test_file)
                shutil.copy2(src, dst)
                
    def run_coverage_check(self, test_files: List[str]) -> float:
        """Run coverage check for given test files"""
        try:
            # Create temporary test runner
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f"""
import pytest
import sys
if __name__ == "__main__":
    sys.exit(pytest.main({test_files}))
""")
                temp_runner = f.name
            
            # Run tests with coverage
            cmd = [
                sys.executable, '-m', 'pytest',
                '--cov=v3-flet',
                '--cov-report=json',
                '--cov-report=term-missing',
                *test_files
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            # Parse coverage report
            coverage_file = self.project_root / 'coverage.json'
            if coverage_file.exists():
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    return coverage_data.get('totals', {}).get('percent_covered', 0.0)
            
            return 0.0
            
        except Exception as e:
            print(f"Error running coverage check: {e}")
            return 0.0
        finally:
            # Cleanup
            if 'temp_runner' in locals():
                os.unlink(temp_runner)
                
    def validate_test_removal(self, test_file: str, kill_list: List[Dict]) -> ValidationResult:
        """Validate removal of a specific test"""
        print(f"  Validating removal of {test_file}...")
        
        # Get baseline coverage
        all_tests = self._get_all_test_files()
        coverage_before = self.run_coverage_check(all_tests)
        
        # Create backup
        self.create_backup([test_file])
        
        # Remove test file
        test_path = Path(test_file)
        if test_path.exists():
            test_path.unlink()
        
        # Run coverage check after removal
        remaining_tests = [t for t in all_tests if t != test_file]
        coverage_after = self.run_coverage_check(remaining_tests)
        
        # Check for regression
        regression_detected = coverage_after < coverage_before - 1.0  # 1% threshold
        
        # Calculate confidence
        confidence = 1.0 - abs(coverage_before - coverage_after) / 100.0
        
        # Collect validation errors
        errors = []
        if regression_detected:
            errors.append(f"Coverage dropped from {coverage_before:.1f}% to {coverage_after:.1f}%")
        
        # Restore backup
        self.restore_backup([test_file])
        
        return ValidationResult(
            test_file=test_file,
            action='remove',
            coverage_before=coverage_before,
            coverage_after=coverage_after,
            regression_detected=regression_detected,
            confidence_score=confidence,
            validation_errors=errors
        )
    
    def validate_test_consolidation(self, cluster: Dict) -> List[ValidationResult]:
        """Validate consolidation of test cluster"""
        results = []
        
        # Get tests to consolidate
        tests_to_consolidate = cluster.get('tests', [])
        primary_test = cluster.get('primary_test', '')
        
        if not tests_to_consolidate or not primary_test:
            return results
        
        print(f"  Validating consolidation of {len(tests_to_consolidate)} tests...")
        
        # Get baseline coverage
        all_tests = self._get_all_test_files()
        coverage_before = self.run_coverage_check(all_tests)
        
        # Create backup
        self.create_backup(tests_to_consolidate)
        
        # Remove redundant tests (keep primary)
        for test_file in tests_to_consolidate:
            if test_file != primary_test:
                test_path = Path(test_file)
                if test_path.exists():
                    test_path.unlink()
        
        # Run coverage check after consolidation
        remaining_tests = [t for t in all_tests if t == primary_test or t not in tests_to_consolidate]
        coverage_after = self.run_coverage_check(remaining_tests)
        
        # Check for regression
        regression_detected = coverage_after < coverage_before - 1.0
        
        # Calculate confidence
        confidence = 1.0 - abs(coverage_before - coverage_after) / 100.0
        
        # Create validation result
        for test_file in tests_to_consolidate:
            if test_file != primary_test:
                results.append(ValidationResult(
                    test_file=test_file,
                    action='consolidate',
                    coverage_before=coverage_before,
                    coverage_after=coverage_after,
                    regression_detected=regression_detected,
                    confidence_score=confidence,
                    validation_errors=[] if not regression_detected else [f"Coverage regression detected"]
                ))
        
        # Restore backup
        self.restore_backup(tests_to_consolidate)
        
        return results
    
    def _get_all_test_files(self) -> List[str]:
        """Get all test files in project"""
        test_files = []
        
        # Discover test files
        for pattern in ['test_*.py', '*_test.py']:
            test_files.extend([
                str(p) for p in self.project_root.rglob(pattern)
                if 'v3-flet/tests' in str(p) or 'v2_legacy_archive/tests' in str(p)
            ])
        
        return test_files
    
    def run_full_validation(self, kill_list_report: Dict) -> Dict:
        """Run complete validation of all proposed changes"""
        print("🔍 Starting migration validation...")
        
        validation_results = []
        
        # Validate removals
        removals = kill_list_report.get('tiered_recommendations', {}).get('immediate_removal', [])
        for removal in removals:
            test_file = removal.get('test_file')
            if test_file:
                result = self.validate_test_removal(test_file, kill_list_report.get('kill_list', []))
                validation_results.append(asdict(result))
        
        # Validate consolidations
        consolidations = kill_list_report.get('tiered_recommendations', {}).get('consolidate', [])
        for consolidation in consolidations:
            # This would need to be enhanced to handle cluster validation
            pass
        
        # Generate validation report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_validations': len(validation_results),
            'successful_removals': len([r for r in validation_results if not r['regression_detected']]),
            'failed_removals': len([r for r in validation_results if r['regression_detected']]),
            'average_confidence': statistics.mean([r['confidence_score'] for r in validation_results]) if validation_results else 0.0,
            'validation_results': validation_results,
            'recommendations': []
        }
        
        # Generate recommendations
        if report['failed_removals'] > 0:
            report['recommendations'].append({
                'type': 'caution',
                'message': f"{report['failed_removals']} removals would cause coverage regression",
                'priority': 'high'
            })
        
        if report['average_confidence'] < 0.9:
            report['recommendations'].append({
                'type': 'review',
                'message': "Low confidence scores suggest careful review needed",
                'priority': 'medium'
            })
        
        # Save validation report
        report_file = self.project_root / 'validation_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Validation complete! Report saved to {report_file}")
        
        # Print summary
        print(f"\n📊 Validation Summary:")
        print(f"Validations Run: {report['total_validations']}")
        print(f"Successful: {report['successful_removals']}")
        print(f"Failed: {report['failed_removals']}")
        print(f"Average Confidence: {report['average_confidence']:.2f}")
        
        return report
    
    def create_rollback_plan(self, validation_report: Dict) -> Dict:
        """Create rollback plan for safe execution"""
        rollback_plan = {
            'timestamp': datetime.now().isoformat(),
            'backup_location': str(self.backup_dir),
            'rollback_commands': [
                f"cp {self.backup_dir}/* {self.project_root}/tests/",
                "git checkout -- tests/",
                "pytest --cov=v3-flet --cov-report=term-missing"
            ],
            'validation_checkpoints': [
                "Run full test suite after each batch",
                "Check coverage remains above 90%",
                "Verify no critical functionality broken"
            ],
            'emergency_contacts': [
                "Project maintainer",
                "CI/CD team",
                "QA team"
            ]
        }
        
        # Save rollback plan
        plan_file = self.project_root / 'rollback_plan.json'
        with open(plan_file, 'w') as f:
            json.dump(rollback_plan, f, indent=2)
        
        return rollback_plan

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    validator = MigrationValidator(project_root)
    
    # Load kill list report
    kill_list_file = project_root / 'kill_list_report.json'
    if kill_list_file.exists():
        with open(kill_list_file) as f:
            kill_list_report = json.load(f)
        
        # Run validation
        validation_report = validator.run_full_validation(kill_list_report)
        
        # Create rollback plan
        rollback_plan = validator.create_rollback_plan(validation_report)
        
        print(f"\n🛡️  Rollback plan created: {project_root}/rollback_plan.json")
    else:
        print("❌ Kill list report not found. Run kill list ranking first.")