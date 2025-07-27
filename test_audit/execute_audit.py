#!/usr/bin/env python3
"""
Surgical Test Audit: Execute Complete Audit
Orchestrates all audit components into a single workflow
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any

# Import all audit components
from coverage_analyzer import TestCoverageAnalyzer
from runtime_profiler import TestRuntimeProfiler
from redundancy_engine import RedundancyEngine
from kill_list_ranker import KillListRanker
from migration_validator import MigrationValidator
from reporting_dashboard import ReportingDashboard

class AuditOrchestrator:
    """Orchestrates the complete surgical test audit workflow"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {}
        
    def discover_test_files(self) -> List[Path]:
        """Discover all test files in project"""
        test_patterns = ['test_*.py', '*_test.py']
        test_files = []
        
        for pattern in test_patterns:
            test_files.extend(self.project_root.rglob(pattern))
            
        # Filter to relevant directories
        relevant_dirs = ['v3-flet/tests', 'v2_legacy_archive/tests']
        filtered = []
        
        for test_file in test_files:
            for dir_name in relevant_dirs:
                if dir_name in str(test_file):
                    filtered.append(test_file)
                    break
                    
        return filtered
    
    def run_complete_audit(self) -> Dict[str, Any]:
        """Execute all phases of the surgical test audit"""
        
        print("🚀 Starting Complete Surgical Test Audit...")
        print("=" * 60)
        
        # Discover test files
        test_files = self.discover_test_files()
        
        # Phase 1: Coverage Analysis
        print("\n📊 Phase 1: Coverage Analysis")
        print("-" * 30)
        coverage_analyzer = TestCoverageAnalyzer(self.project_root)
        coverage_report = coverage_analyzer.run_full_audit()
        self.results['coverage'] = coverage_report
        
        # Phase 2: Runtime Profiling
        print("\n⏱️ Phase 2: Runtime Profiling")
        print("-" * 30)
        profiler = TestRuntimeProfiler(self.project_root)
        performance_report = profiler.run_runtime_audit(test_files)
        self.results['performance'] = performance_report
        
        # Phase 3: Redundancy Analysis
        print("\n🔄 Phase 3: Redundancy Analysis")
        print("-" * 30)
        redundancy_engine = RedundancyEngine(self.project_root)
        redundancy_report = redundancy_engine.analyze_redundancy()
        self.results['redundancy'] = redundancy_report
        
        # Phase 4: Kill List Generation
        print("\n🎯 Phase 4: Kill List Generation")
        print("-" * 30)
        kill_ranker = KillListRanker(self.project_root)
        kill_list = kill_ranker.generate_surgical_recommendations()
        self.results['kill_list'] = kill_list
        
        # Phase 5: Validation
        print("\n✅ Phase 5: Validation")
        print("-" * 30)
        validator = MigrationValidator(self.project_root)
        validation_report = validator.validate_migration_plan(kill_list)
        self.results['validation'] = validation_report
        
        # Phase 6: Reporting
        print("\n📈 Phase 6: Reporting")
        print("-" * 30)
        dashboard = ReportingDashboard(self.project_root)
        dashboard.generate_comprehensive_report(self.results)
        
        return self.results
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate executive summary of audit results"""
        
        kill_list = self.results.get('kill_list', {})
        validation = self.results.get('validation', {})
        
        total_tests = len(self.results.get('coverage', {}).get('test_mappings', {}))
        tests_to_remove = len(kill_list.get('tiered_recommendations', {}).get('immediate_removal', []))
        tests_to_consolidate = len(kill_list.get('tiered_recommendations', {}).get('consolidate', []))
        
        estimated_runtime_reduction = sum(
            item.get('avg_duration', 0) 
            for item in kill_list.get('tiered_recommendations', {}).get('immediate_removal', [])
        )
        
        return {
            'audit_summary': {
                'total_tests_analyzed': total_tests,
                'tests_recommended_for_removal': tests_to_remove,
                'tests_recommended_for_consolidation': tests_to_consolidate,
                'estimated_runtime_reduction_seconds': estimated_runtime_reduction,
                'estimated_runtime_reduction_percentage': (estimated_runtime_reduction / 300.0) * 100,  # Assuming 5min baseline
                'confidence_level': validation.get('confidence_level', 0.0),
                'risk_assessment': validation.get('risk_level', 'UNKNOWN')
            },
            'top_removals': kill_list.get('tiered_recommendations', {}).get('immediate_removal', [])[:10],
            'implementation_plan': self._generate_implementation_plan(kill_list)
        }
    
    def _generate_implementation_plan(self, kill_list: Dict) -> List[Dict]:
        """Generate phased implementation plan for test removals"""
        
        plan = []
        
        # Phase 1: Low-risk removals (high redundancy, low unique value)
        immediate_removal = kill_list.get('tiered_recommendations', {}).get('immediate_removal', [])
        if immediate_removal:
            plan.append({
                'phase': 1,
                'description': 'Remove high-confidence redundant tests',
                'tests': immediate_removal[:5],
                'estimated_savings': len(immediate_removal[:5]),
                'rollback_plan': 'Restore from git backup'
            })
        
        # Phase 2: Medium-risk consolidations
        consolidate = kill_list.get('tiered_recommendations', {}).get('consolidate', [])
        if consolidate:
            plan.append({
                'phase': 2,
                'description': 'Consolidate medium-confidence overlapping tests',
                'tests': consolidate[:3],
                'estimated_savings': len(consolidate[:3]),
                'rollback_plan': 'Restore individual tests if issues arise'
            })
        
        # Phase 3: High-risk removals (requires careful validation)
        review_manually = kill_list.get('tiered_recommendations', {}).get('review_manually', [])
        if review_manually:
            plan.append({
                'phase': 3,
                'description': 'Manual review of remaining tests',
                'tests': review_manually[:2],
                'estimated_savings': 0,  # Manual review
                'rollback_plan': 'Full test suite rollback capability'
            })
        
        return plan

def main():
    """Main entry point for the audit orchestrator"""
    
    project_root = Path(__file__).parent.parent
    orchestrator = AuditOrchestrator(project_root)
    
    try:
        # Run complete audit
        results = orchestrator.run_complete_audit()
        
        # Generate summary
        summary = orchestrator.generate_summary_report()
        
        # Save final results
        final_report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'audit_results': results,
            'summary': summary,
            'next_steps': [
                "Review the generated dashboard at test_audit_reports/dashboard.html",
                "Examine individual test recommendations in final_recommendations.json",
                "Implement Phase 1 removals (low-risk) using provided validation framework",
                "Monitor test suite health after each phase",
                "Adjust implementation based on monitoring results"
            ]
        }
        
        # Save final report
        report_file = project_root / 'test_audit_reports' / 'final_audit_report.json'
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(final_report, f, indent=2, default=str)
        
        print("\n" + "=" * 60)
        print("🎉 SURGICAL TEST AUDIT COMPLETE!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   Total tests analyzed: {summary['audit_summary']['total_tests_analyzed']}")
        print(f"   Tests to remove: {summary['audit_summary']['tests_recommended_for_removal']}")
        print(f"   Tests to consolidate: {summary['audit_summary']['tests_recommended_for_consolidation']}")
        print(f"   Estimated runtime reduction: {summary['audit_summary']['estimated_runtime_reduction_percentage']:.1f}%")
        
        print(f"\n📁 Reports generated:")
        print(f"   - Interactive dashboard: test_audit_reports/dashboard.html")
        print(f"   - Final report: {report_file}")
        
        print(f"\n🎯 Next steps:")
        print("   1. Review the generated dashboard at test_audit_reports/dashboard.html")
        print("   2. Examine individual test recommendations in final_recommendations.json")
        print("   3. Implement Phase 1 removals (low-risk) using provided validation framework")
        print("   4. Monitor test suite health after each phase")
        print("   5. Adjust implementation based on monitoring results")
        
    except Exception as e:
        print(f"\n❌ Error during audit: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())