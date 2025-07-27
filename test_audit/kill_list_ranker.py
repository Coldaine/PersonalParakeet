#!/usr/bin/env python3
"""
Surgical Test Audit: Kill-List Ranking Algorithm
Ranks tests for removal based on comprehensive analysis
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import statistics
from datetime import datetime

@dataclass
class TestScore:
    """Comprehensive score for test removal"""
    test_file: str
    test_name: str
    removal_score: float
    coverage_score: float
    redundancy_score: float
    performance_score: float
    maintenance_score: float
    risk_level: str
    removal_reason: str
    confidence: float

class KillListRanker:
    """Ranks tests for surgical removal based on multi-factor analysis"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scores = []
        
    def load_analysis_reports(self) -> Dict:
        """Load all analysis reports"""
        reports = {}
        
        # Load coverage report
        coverage_file = self.project_root / 'test_audit_report.json'
        if coverage_file.exists():
            with open(coverage_file) as f:
                reports['coverage'] = json.load(f)
        
        # Load runtime report
        runtime_file = self.project_root / 'runtime_audit_report.json'
        if runtime_file.exists():
            with open(runtime_file) as f:
                reports['runtime'] = json.load(f)
        
        # Load redundancy report
        redundancy_file = self.project_root / 'redundancy_report.json'
        if redundancy_file.exists():
            with open(redundancy_file) as f:
                reports['redundancy'] = json.load(f)
        
        return reports
    
    def calculate_coverage_score(self, test_data: Dict) -> float:
        """Score based on unique coverage contribution"""
        # Lower score = more redundant
        if 'redundancy' in test_data:
            redundancy = test_data['redundancy']
            return 1.0 - redundancy.get('overlap_score', 0.0)
        return 1.0
    
    def calculate_redundancy_score(self, test_data: Dict) -> float:
        """Score based on redundancy with other tests"""
        # Higher score = more redundant
        if 'redundancy' in test_data:
            return test_data['redundancy'].get('overlap_score', 0.0)
        return 0.0
    
    def calculate_performance_score(self, test_data: Dict) -> float:
        """Score based on performance issues"""
        score = 0.0
        
        if 'runtime' in test_data:
            runtime = test_data['runtime']
            
            # Slow execution penalty
            duration = runtime.get('avg_duration', 0.0)
            if duration > 10.0:
                score += 0.8
            elif duration > 5.0:
                score += 0.5
            elif duration > 2.0:
                score += 0.2
            
            # Flakiness penalty
            flakiness = runtime.get('flakiness_score', 0.0)
            score += flakiness
            
            # Performance trend penalty
            trend = runtime.get('performance_trend', 'stable')
            if trend == 'degrading':
                score += 0.3
            elif trend == 'unstable':
                score += 0.5
        
        return min(score, 1.0)
    
    def calculate_maintenance_score(self, test_data: Dict) -> float:
        """Score based on maintenance burden"""
        score = 0.0
        
        # File age factor (older = higher maintenance)
        if 'file_stats' in test_data:
            age_days = test_data['file_stats'].get('age_days', 0)
            if age_days > 365:
                score += 0.3
            elif age_days > 180:
                score += 0.2
        
        # Complexity factor
        if 'complexity' in test_data:
            complexity = test_data['complexity'].get('cyclomatic_complexity', 0)
            if complexity > 10:
                score += 0.4
            elif complexity > 5:
                score += 0.2
        
        return min(score, 1.0)
    
    def determine_risk_level(self, scores: Dict[str, float]) -> str:
        """Determine risk level for removal"""
        total_score = sum(scores.values())
        
        if total_score > 2.5:
            return 'low'
        elif total_score > 1.5:
            return 'medium'
        else:
            return 'high'
    
    def generate_removal_reason(self, scores: Dict[str, float]) -> str:
        """Generate specific reason for removal recommendation"""
        reasons = []
        
        if scores['redundancy_score'] > 0.7:
            reasons.append("highly redundant")
        
        if scores['performance_score'] > 0.7:
            reasons.append("performance issues")
        
        if scores['maintenance_score'] > 0.5:
            reasons.append("maintenance burden")
        
        if scores['coverage_score'] < 0.3:
            reasons.append("low unique coverage")
        
        if not reasons:
            return "general optimization"
        
        return ", ".join(reasons)
    
    def rank_tests_for_removal(self) -> List[TestScore]:
        """Generate ranked kill list"""
        reports = self.load_analysis_reports()
        scores = []
        
        # Get all test files
        test_files = set()
        
        if 'coverage' in reports:
            for mapping in reports['coverage'].get('test_mappings', {}).values():
                test_files.add(mapping['test_file'])
        
        if 'runtime' in reports:
            for profile in reports['runtime'].get('profiles', {}).values():
                test_files.add(profile['test_file'])
        
        # Score each test
        for test_file in test_files:
            test_name = Path(test_file).stem
            
            # Collect all data for this test
            test_data = {
                'coverage': {},
                'runtime': {},
                'redundancy': {},
                'file_stats': {}
            }
            
            # Extract coverage data
            if 'coverage' in reports:
                for key, mapping in reports['coverage'].get('test_mappings', {}).items():
                    if mapping['test_file'] == test_file:
                        test_data['coverage'] = mapping
                        break
            
            # Extract runtime data
            if 'runtime' in reports:
                for key, profile in reports['runtime'].get('profiles', {}).items():
                    if profile['test_file'] == test_file:
                        test_data['runtime'] = profile
                        break
            
            # Extract redundancy data
            if 'redundancy' in reports:
                for cluster in reports['redundancy'].get('clusters', []):
                    if test_file in cluster.get('tests', []):
                        test_data['redundancy'] = cluster
                        break
            
            # Calculate individual scores
            coverage_score = self.calculate_coverage_score(test_data)
            redundancy_score = self.calculate_redundancy_score(test_data)
            performance_score = self.calculate_performance_score(test_data)
            maintenance_score = self.calculate_maintenance_score(test_data)
            
            # Calculate overall removal score (higher = better candidate)
            removal_score = (
                redundancy_score * 0.4 +
                performance_score * 0.3 +
                maintenance_score * 0.2 +
                (1.0 - coverage_score) * 0.1
            )
            
            # Determine risk and reason
            risk_level = self.determine_risk_level({
                'coverage': coverage_score,
                'redundancy': redundancy_score,
                'performance': performance_score,
                'maintenance': maintenance_score
            })
            
            removal_reason = self.generate_removal_reason({
                'coverage': coverage_score,
                'redundancy': redundancy_score,
                'performance': performance_score,
                'maintenance': maintenance_score
            })
            
            # Calculate confidence based on data completeness
            data_completeness = sum([
                1 if test_data['coverage'] else 0,
                1 if test_data['runtime'] else 0,
                1 if test_data['redundancy'] else 0
            ]) / 3.0
            
            score = TestScore(
                test_file=test_file,
                test_name=test_name,
                removal_score=removal_score,
                coverage_score=coverage_score,
                redundancy_score=redundancy_score,
                performance_score=performance_score,
                maintenance_score=maintenance_score,
                risk_level=risk_level,
                removal_reason=removal_reason,
                confidence=data_completeness
            )
            
            scores.append(score)
        
        # Sort by removal score (descending)
        scores.sort(key=lambda x: x.removal_score, reverse=True)
        
        return scores
    
    def generate_kill_list_report(self, scores: List[TestScore]) -> Dict:
        """Generate comprehensive kill list report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_tests_analyzed': len(scores),
            'tests_recommended_for_removal': len([s for s in scores if s.removal_score > 0.7]),
            'tests_recommended_for_consolidation': len([s for s in scores if 0.5 < s.removal_score <= 0.7]),
            'estimated_reduction': len([s for s in scores if s.removal_score > 0.5]),
            'confidence_distribution': {
                'high': len([s for s in scores if s.confidence > 0.8]),
                'medium': len([s for s in scores if 0.5 < s.confidence <= 0.8]),
                'low': len([s for s in scores if s.confidence <= 0.5])
            },
            'kill_list': [asdict(s) for s in scores],
            'tiered_recommendations': {
                'immediate_removal': [asdict(s) for s in scores if s.removal_score > 0.8 and s.risk_level == 'low'],
                'consolidate': [asdict(s) for s in scores if 0.6 < s.removal_score <= 0.8],
                'review_manually': [asdict(s) for s in scores if s.removal_score <= 0.6 or s.risk_level == 'high']
            },
            'implementation_plan': {
                'phase1': {
                    'description': 'Remove high-confidence redundant tests',
                    'tests': [s.test_file for s in scores if s.removal_score > 0.8 and s.risk_level == 'low'],
                    'estimated_savings': len([s for s in scores if s.removal_score > 0.8 and s.risk_level == 'low'])
                },
                'phase2': {
                    'description': 'Consolidate medium-confidence tests',
                    'tests': [s.test_file for s in scores if 0.6 < s.removal_score <= 0.8],
                    'estimated_savings': len([s for s in scores if 0.6 < s.removal_score <= 0.8])
                },
                'phase3': {
                    'description': 'Manual review of remaining tests',
                    'tests': [s.test_file for s in scores if s.removal_score <= 0.6 or s.risk_level == 'high'],
                    'estimated_savings': 0  # Manual review
                }
            }
        }
        
        return report
    
    def generate_surgical_recommendations(self) -> Dict:
        """Generate final surgical recommendations"""
        print("🎯 Generating surgical kill list...")
        
        # Rank all tests
        scores = self.rank_tests_for_removal()
        
        # Generate report
        report = self.generate_kill_list_report(scores)
        
        # Save report
        report_file = self.project_root / 'kill_list_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)
        
        print(f"\n✅ Kill list generated! Report saved to {report_file}")
        
        # Print summary
        print(f"\n📊 Kill List Summary:")
        print(f"Total Tests: {report['total_tests_analyzed']}")
        print(f"Tests to Remove: {report['tests_recommended_for_removal']}")
        print(f"Tests to Consolidate: {report['tests_recommended_for_consolidation']}")
        print(f"Estimated Reduction: {report['estimated_reduction']} tests")
        
        if report['tiered_recommendations']['immediate_removal']:
            print(f"\n🎯 Immediate Removal Candidates:")
            for test in report['tiered_recommendations']['immediate_removal'][:5]:
                print(f"  {test['test_name']} (score: {test['removal_score']:.2f}) - {test['removal_reason']}")
        
        return report

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    ranker = KillListRanker(project_root)
    
    # Generate surgical recommendations
    report = ranker.generate_surgical_recommendations()