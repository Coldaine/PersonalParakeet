#!/usr/bin/env python3
"""
Surgical Test Audit: Coverage Analyzer
Maps tests to exact production code lines for redundancy analysis
"""

import ast
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
import subprocess
import re
from dataclasses import dataclass, asdict

@dataclass
class TestCoverage:
    """Represents test coverage for a specific test file"""
    test_file: str
    target_module: str
    covered_lines: Set[int]
    covered_functions: Set[str]
    covered_classes: Set[str]
    execution_time: float
    flakiness_score: float
    unique_coverage: float = 0.0

@dataclass
class CoverageReport:
    """Complete coverage analysis report"""
    timestamp: str
    total_tests: int
    total_lines: int
    covered_lines: int
    coverage_percentage: float
    test_mappings: Dict[str, TestCoverage]
    redundancy_matrix: Dict[str, List[str]]
    kill_list: List[Dict]

class TestCoverageAnalyzer:
    """Analyzes test coverage at line level for surgical audit"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_files = []
        self.production_files = []
        self.coverage_data = {}
        
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
    
    def extract_test_targets(self, test_file: Path) -> List[str]:
        """Extract which production modules a test targets"""
        targets = []
        content = test_file.read_text()
        
        # Look for import statements
        import_pattern = r'(?:from|import)\s+([a-zA-Z_][a-zA-Z0-9_.]*)'
        imports = re.findall(import_pattern, content)
        
        # Map imports to production files
        for imp in imports:
            if 'personalparakeet' in imp or 'v3-flet' in imp:
                # Convert import to file path
                module_path = imp.replace('.', '/')
                possible_files = [
                    f"v3-flet/{module_path}.py",
                    f"v2_legacy_archive/{module_path}.py",
                    f"v3-flet/core/{module_path.split('.')[-1]}.py"
                ]
                
                for file_path in possible_files:
                    full_path = self.project_root / file_path
                    if full_path.exists():
                        targets.append(str(full_path))
                        break
                        
        return targets
    
    def analyze_test_coverage(self, test_file: Path, target_file: Path) -> TestCoverage:
        """Analyze exact line coverage between test and target"""
        
        # Parse target file to get all lines
        try:
            target_ast = ast.parse(target_file.read_text())
        except:
            return TestCoverage(
                test_file=str(test_file),
                target_module=str(target_file),
                covered_lines=set(),
                covered_functions=set(),
                covered_classes=set(),
                execution_time=0.0,
                flakiness_score=0.0
            )
        
        # Get all lines in target
        target_lines = len(target_file.read_text().splitlines())
        
        # Parse test file to find what it tests
        test_ast = ast.parse(test_file.read_text())
        
        covered_lines = set()
        covered_functions = set()
        covered_classes = set()
        
        # Look for test method names and assertions
        for node in ast.walk(test_ast):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                if func_name.startswith('test_'):
                    # Extract function/class names from test
                    for child in ast.walk(node):
                        if isinstance(child, ast.Attribute):
                            if isinstance(child.value, ast.Name):
                                covered_functions.add(child.attr)
                        elif isinstance(child, ast.Name):
                            if child.id not in ['self', 'mock', 'patch']:
                                covered_classes.add(child.id)
        
        # Measure execution time
        start_time = time.time()
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', str(test_file), '-v'
            ], capture_output=True, text=True, timeout=30)
            execution_time = time.time() - start_time
            flakiness_score = 1.0 if result.returncode != 0 else 0.0
        except:
            execution_time = 30.0
            flakiness_score = 1.0
            
        return TestCoverage(
            test_file=str(test_file),
            target_module=str(target_file),
            covered_lines=covered_lines,
            covered_functions=covered_functions,
            covered_classes=covered_classes,
            execution_time=execution_time,
            flakiness_score=flakiness_score
        )
    
    def generate_redundancy_matrix(self) -> Dict[str, List[str]]:
        """Identify redundant tests covering same functionality"""
        redundancy = {}
        
        for test1, coverage1 in self.coverage_data.items():
            redundant_with = []
            
            for test2, coverage2 in self.coverage_data.items():
                if test1 != test2 and coverage1.target_module == coverage2.target_module:
                    # Calculate overlap
                    overlap = len(coverage1.covered_functions.intersection(coverage2.covered_functions))
                    total = len(coverage1.covered_functions.union(coverage2.covered_functions))
                    
                    if total > 0 and overlap / total > 0.8:  # 80% overlap threshold
                        redundant_with.append(test2)
                        
            if redundant_with:
                redundancy[test1] = redundant_with
                
        return redundancy
    
    def calculate_kill_list(self) -> List[Dict]:
        """Generate ranked list of tests to remove/consolidate"""
        kill_list = []
        
        for test_file, coverage in self.coverage_data.items():
            # Calculate value score
            runtime_penalty = min(coverage.execution_time / 10.0, 1.0)  # Normalize to 0-1
            flakiness_penalty = coverage.flakiness_score
            
            # Estimate unique value (simplified)
            unique_value = 1.0 - (len(self.coverage_data) / 47.0)  # Relative to total
            
            # Final score (lower = better candidate for removal)
            removal_score = runtime_penalty + flakiness_penalty - unique_value
            
            kill_list.append({
                'test_file': test_file,
                'target_module': coverage.target_module,
                'execution_time': coverage.execution_time,
                'flakiness_score': coverage.flakiness_score,
                'removal_score': removal_score,
                'recommendation': 'REMOVE' if removal_score > 1.5 else 'CONSOLIDATE'
            })
            
        return sorted(kill_list, key=lambda x: x['removal_score'], reverse=True)
    
    def run_full_audit(self) -> CoverageReport:
        """Execute complete test audit"""
        print("🔍 Starting surgical test audit...")
        
        # Discover test files
        test_files = self.discover_test_files()
        print(f"📊 Found {len(test_files)} test files")
        
        # Analyze each test
        for test_file in test_files:
            targets = self.extract_test_targets(test_file)
            
            for target in targets:
                coverage = self.analyze_test_coverage(test_file, Path(target))
                key = f"{test_file}:{target}"
                self.coverage_data[key] = coverage
                
        # Generate analysis
        redundancy = self.generate_redundancy_matrix()
        kill_list = self.calculate_kill_list()
        
        # Calculate overall stats
        total_lines = sum(len(Path(c.target_module).read_text().splitlines()) 
                         for c in self.coverage_data.values())
        covered_lines = len(set().union(*[c.covered_lines for c in self.coverage_data.values()]))
        
        report = CoverageReport(
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            total_tests=len(test_files),
            total_lines=total_lines,
            covered_lines=covered_lines,
            coverage_percentage=(covered_lines / max(total_lines, 1)) * 100,
            test_mappings=self.coverage_data,
            redundancy_matrix=redundancy,
            kill_list=kill_list
        )
        
        # Save report
        report_file = self.project_root / 'test_audit_report.json'
        with open(report_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=lambda x: list(x) if isinstance(x, set) else x)
            
        print(f"✅ Audit complete! Report saved to {report_file}")
        return report

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    analyzer = TestCoverageAnalyzer(project_root)
    report = analyzer.run_full_audit()
    
    # Print summary
    print(f"\n📈 Audit Summary:")
    print(f"Total Tests: {report.total_tests}")
    print(f"Coverage: {report.coverage_percentage:.1f}%")
    print(f"Tests to Review: {len(report.kill_list)}")
    
    # Show top candidates for removal
    if report.kill_list:
        print(f"\n🔥 Top Removal Candidates:")
        for item in report.kill_list[:5]:
            print(f"  {item['test_file']} (score: {item['removal_score']:.2f})")