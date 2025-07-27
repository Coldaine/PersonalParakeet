#!/usr/bin/env python3
"""
Surgical Test Audit: Redundancy Analysis Engine
Identifies overlapping test coverage and suggests consolidation opportunities
"""

import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, asdict
import networkx as nx
from collections import defaultdict
import difflib

@dataclass
class TestOverlap:
    """Represents overlap between two tests"""
    test1: str
    test2: str
    overlap_score: float
    shared_functions: Set[str]
    shared_classes: Set[str]
    shared_assertions: Set[str]
    consolidation_potential: str  # 'high', 'medium', 'low'

@dataclass
class RedundancyCluster:
    """Group of highly redundant tests"""
    cluster_id: str
    tests: List[str]
    primary_test: str
    overlap_matrix: Dict[str, Dict[str, float]]
    consolidation_strategy: str

class RedundancyAnalyzer:
    """Analyzes test redundancy and suggests consolidation"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_functions = {}
        self.test_assertions = {}
        self.overlaps = []
        self.clusters = []
        
    def extract_test_functions(self, test_file: Path) -> Dict[str, Dict]:
        """Extract functions and assertions from test file"""
        try:
            content = test_file.read_text()
            tree = ast.parse(content)
            
            functions = {}
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_'):
                        # Extract function body
                        body_start = node.body[0].lineno if node.body else node.lineno
                        body_end = node.body[-1].lineno if node.body else node.lineno
                        
                        # Extract assertions
                        assertions = []
                        for child in ast.walk(node):
                            if isinstance(child, ast.Assert):
                                assertions.append(ast.unparse(child))
                            elif isinstance(child, ast.Call):
                                if isinstance(child.func, ast.Attribute):
                                    if child.func.attr in ['assertEqual', 'assertTrue', 'assertFalse', 'assertIn', 'assertNotIn']:
                                        assertions.append(ast.unparse(child))
                        
                        # Extract setup code
                        setup_code = []
                        for stmt in node.body[:3]:  # First 3 statements
                            if isinstance(stmt, (ast.Assign, ast.Import, ast.ImportFrom)):
                                setup_code.append(ast.unparse(stmt))
                        
                        functions[node.name] = {
                            'name': node.name,
                            'file': str(test_file),
                            'assertions': assertions,
                            'setup_code': setup_code,
                            'lines': (node.lineno, node.end_lineno or node.lineno),
                            'complexity': len(assertions) + len(setup_code)
                        }
                        
            return functions
            
        except Exception as e:
            print(f"Error parsing {test_file}: {e}")
            return {}
    
    def calculate_overlap_score(self, test1: Dict, test2: Dict) -> float:
        """Calculate overlap score between two tests"""
        # Assertion overlap
        assertion_overlap = len(set(test1['assertions']).intersection(set(test2['assertions'])))
        total_assertions = len(set(test1['assertions']).union(set(test2['assertions'])))
        
        assertion_score = assertion_overlap / max(total_assertions, 1)
        
        # Setup code overlap
        setup_overlap = len(set(test1['setup_code']).intersection(set(test2['setup_code'])))
        total_setup = len(set(test1['setup_code']).union(set(test2['setup_code'])))
        
        setup_score = setup_overlap / max(total_setup, 1)
        
        # Complexity similarity (prefer consolidating similar complexity)
        complexity_diff = abs(test1['complexity'] - test2['complexity'])
        complexity_score = 1 - (complexity_diff / max(test1['complexity'], test2['complexity'], 1))
        
        # Weighted combination
        return (assertion_score * 0.5 + setup_score * 0.3 + complexity_score * 0.2)
    
    def find_redundant_tests(self, test_files: List[Path]) -> List[TestOverlap]:
        """Find all redundant test pairs"""
        overlaps = []
        
        # Extract all test functions
        all_tests = {}
        for test_file in test_files:
            functions = self.extract_test_functions(test_file)
            all_tests.update(functions)
        
        # Compare all pairs
        test_names = list(all_tests.keys())
        
        for i, test1 in enumerate(test_names):
            for test2 in test_names[i+1:]:
                score = self.calculate_overlap_score(all_tests[test1], all_tests[test2])
                
                if score > 0.3:  # 30% overlap threshold
                    # Extract shared elements
                    shared_assertions = set(all_tests[test1]['assertions']).intersection(
                        set(all_tests[test2]['assertions'])
                    )
                    shared_setup = set(all_tests[test1]['setup_code']).intersection(
                        set(all_tests[test2]['setup_code'])
                    )
                    
                    # Determine consolidation potential
                    if score > 0.8:
                        potential = 'high'
                    elif score > 0.6:
                        potential = 'medium'
                    else:
                        potential = 'low'
                    
                    overlap = TestOverlap(
                        test1=test1,
                        test2=test2,
                        overlap_score=score,
                        shared_functions=set(),  # Could be enhanced
                        shared_classes=set(),    # Could be enhanced
                        shared_assertions=shared_assertions,
                        consolidation_potential=potential
                    )
                    
                    overlaps.append(overlap)
        
        return overlaps
    
    def build_redundancy_graph(self, overlaps: List[TestOverlap]) -> nx.Graph:
        """Build graph of test redundancies"""
        G = nx.Graph()
        
        for overlap in overlaps:
            G.add_edge(overlap.test1, overlap.test2, weight=overlap.overlap_score)
        
        return G
    
    def find_clusters(self, graph: nx.Graph) -> List[RedundancyCluster]:
        """Find clusters of highly redundant tests"""
        clusters = []
        
        # Use connected components for initial clustering
        components = list(nx.connected_components(graph))
        
        for i, component in enumerate(components):
            if len(component) > 1:
                # Create cluster
                cluster_tests = list(component)
                
                # Find primary test (highest connectivity)
                primary = max(cluster_tests, key=lambda t: len(list(graph.neighbors(t))))
                
                # Build overlap matrix
                matrix = {}
                for test1 in cluster_tests:
                    matrix[test1] = {}
                    for test2 in cluster_tests:
                        if test1 != test2 and graph.has_edge(test1, test2):
                            matrix[test1][test2] = graph[test1][test2]['weight']
                        else:
                            matrix[test1][test2] = 0.0
                
                # Determine consolidation strategy
                if len(cluster_tests) <= 3:
                    strategy = 'merge_into_primary'
                elif len(cluster_tests) <= 5:
                    strategy = 'create_parameterized_test'
                else:
                    strategy = 'create_test_class'
                
                cluster = RedundancyCluster(
                    cluster_id=f"cluster_{i}",
                    tests=cluster_tests,
                    primary_test=primary,
                    overlap_matrix=matrix,
                    consolidation_strategy=strategy
                )
                
                clusters.append(cluster)
        
        return clusters
    
    def generate_consolidation_plan(self, clusters: List[RedundancyCluster]) -> List[Dict]:
        """Generate actionable consolidation recommendations"""
        plans = []
        
        for cluster in clusters:
            plan = {
                'cluster_id': cluster.cluster_id,
                'tests_affected': len(cluster.tests),
                'primary_test': cluster.primary_test,
                'strategy': cluster.consolidation_strategy,
                'estimated_savings': len(cluster.tests) - 1,  # Tests removed
                'implementation_steps': [],
                'risk_level': 'low' if len(cluster.tests) <= 3 else 'medium'
            }
            
            # Generate specific steps based on strategy
            if cluster.consolidation_strategy == 'merge_into_primary':
                plan['implementation_steps'] = [
                    f"Extend {cluster.primary_test} to cover all scenarios",
                    f"Remove redundant tests: {', '.join([t for t in cluster.tests if t != cluster.primary_test])}",
                    "Update test assertions to be more comprehensive"
                ]
                
            elif cluster.consolidation_strategy == 'create_parameterized_test':
                plan['implementation_steps'] = [
                    "Create parameterized test covering all scenarios",
                    "Extract common setup into fixtures",
                    f"Replace {len(cluster.tests)} tests with single parameterized test",
                    "Update test data to cover edge cases"
                ]
                
            elif cluster.consolidation_strategy == 'create_test_class':
                plan['implementation_steps'] = [
                    "Create test class with shared setup",
                    "Split tests into logical methods",
                    "Use class-level fixtures for common setup",
                    "Implement inheritance for shared functionality"
                ]
            
            plans.append(plan)
        
        return plans
    
    def analyze_redundancy(self, test_files: List[Path]) -> Dict:
        """Execute complete redundancy analysis"""
        print("🔍 Starting redundancy analysis...")
        
        # Find all overlaps
        overlaps = self.find_redundant_tests(test_files)
        print(f"📊 Found {len(overlaps)} redundant test pairs")
        
        # Build redundancy graph
        graph = self.build_redundancy_graph(overlaps)
        
        # Find clusters
        clusters = self.find_clusters(graph)
        print(f"🎯 Identified {len(clusters)} redundancy clusters")
        
        # Generate consolidation plans
        plans = self.generate_consolidation_plan(clusters)
        
        # Calculate potential savings
        total_tests_removed = sum(p['estimated_savings'] for p in plans)
        
        report = {
            'timestamp': str(Path().cwd()),
            'total_redundant_pairs': len(overlaps),
            'total_clusters': len(clusters),
            'potential_tests_removed': total_tests_removed,
            'reduction_percentage': (total_tests_removed / len(test_files)) * 100 if test_files else 0,
            'clusters': [asdict(c) for c in clusters],
            'consolidation_plans': plans,
            'high_priority_clusters': [p for p in plans if p['risk_level'] == 'low']
        }
        
        # Save report
        report_file = self.project_root / 'redundancy_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)
        
        print(f"\n✅ Redundancy analysis complete! Report saved to {report_file}")
        
        # Print summary
        print(f"\n📈 Redundancy Summary:")
        print(f"Redundant Pairs: {len(overlaps)}")
        print(f"Clusters Found: {len(clusters)}")
        print(f"Tests to Remove: {total_tests_removed}")
        print(f"Reduction: {report['reduction_percentage']:.1f}%")
        
        if report['high_priority_clusters']:
            print(f"\n🎯 High Priority Consolidations:")
            for cluster in report['high_priority_clusters'][:3]:
                print(f"  {cluster['cluster_id']}: {cluster['tests_affected']} tests → 1 test")
        
        return report

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    analyzer = RedundancyAnalyzer(project_root)
    
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
    
    # Run redundancy analysis
    report = analyzer.analyze_redundancy(filtered)