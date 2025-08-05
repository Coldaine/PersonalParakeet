#!/usr/bin/env python3
"""
Interactive Test Visualization Dashboard for PersonalParakeet

This script provides a comprehensive dashboard for visualizing test structure,
coverage, and execution results with interactive charts and real-time monitoring.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import threading
import time

try:
    import flet as ft
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import seaborn as sns
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(f"Warning: {e}. Some visualization features may be limited.")
    ft = None
    plt = None
    sns = None
    pd = None
    np = None

class TestVisualizationDashboard:
    """Interactive dashboard for test visualization and monitoring."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_dirs = [
            self.project_root / "tests",
            self.project_root / "src/personalparakeet/tests"
        ]
        self.current_test_process = None
        self.test_results = {}
        self.coverage_data = {}
        
    def analyze_test_structure(self) -> Dict[str, Any]:
        """Analyze the test structure and return comprehensive data."""
        structure = {
            "test_categories": {},
            "test_files": [],
            "test_methods": [],
            "markers": {},
            "total_tests": 0,
            "structure_tree": {}
        }
        
        # Define test categories and their paths
        categories = {
            "unit": ["tests/unit"],
            "hardware": ["tests/hardware"],
            "integration": ["tests/integration"],
            "interactive": ["src/personalparakeet/tests/utilities"],
            "benchmarks": ["tests/benchmarks"],
            "core": ["tests/core"]
        }
        
        for category, paths in categories.items():
            structure["test_categories"][category] = {
                "paths": paths,
                "files": [],
                "methods": [],
                "count": 0
            }
            
            for path in paths:
                full_path = self.project_root / path
                if full_path.exists():
                    for test_file in full_path.glob("test_*.py"):
                        structure["test_categories"][category]["files"].append(str(test_file))
                        structure["test_files"].append(str(test_file))
                        
                        # Count test methods (simplified)
                        try:
                            with open(test_file, 'r') as f:
                                content = f.read()
                                method_count = content.count("def test_")
                                structure["test_categories"][category]["methods"].append(method_count)
                                structure["test_methods"].append(method_count)
                                structure["test_categories"][category]["count"] += method_count
                                structure["total_tests"] += method_count
                        except Exception:
                            pass
        
        # Build structure tree
        structure["structure_tree"] = self._build_structure_tree()
        
        return structure
    
    def _build_structure_tree(self) -> Dict[str, Any]:
        """Build a hierarchical structure tree."""
        tree = {
            "name": "PersonalParakeet Tests",
            "type": "root",
            "children": []
        }
        
        # Main tests
        main_tests = {
            "name": "Main Test Suite",
            "type": "directory",
            "path": "tests",
            "children": [
                {"name": "Unit Tests", "type": "category", "path": "tests/unit", "count": 0},
                {"name": "Hardware Tests", "type": "category", "path": "tests/hardware", "count": 0},
                {"name": "Integration Tests", "type": "category", "path": "tests/integration", "count": 0},
                {"name": "Core Infrastructure", "type": "category", "path": "tests/core", "count": 0},
                {"name": "Benchmarks", "type": "category", "path": "tests/benchmarks", "count": 0}
            ]
        }
        
        # Application tests
        app_tests = {
            "name": "Application Tests",
            "type": "directory", 
            "path": "src/personalparakeet/tests",
            "children": [
                {"name": "Utility Scripts", "type": "category", "path": "src/personalparakeet/tests/utilities", "count": 0}
            ]
        }
        
        tree["children"].extend([main_tests, app_tests])
        
        # Count actual files
        for child in main_tests["children"]:
            path = self.project_root / child["path"]
            if path.exists():
                child["count"] = len(list(path.glob("test_*.py")))
        
        for child in app_tests["children"]:
            path = self.project_root / child["path"]
            if path.exists():
                child["count"] = len(list(path.glob("*.py")))
        
        return tree
    
    def analyze_coverage(self) -> Dict[str, Any]:
        """Analyze test coverage data."""
        coverage_file = self.project_root / ".coverage"
        coverage_data = {
            "has_coverage": coverage_file.exists(),
            "coverage_file": str(coverage_file),
            "coverage_percentage": 0,
            "covered_files": [],
            "uncovered_files": [],
            "coverage_by_module": {}
        }
        
        if coverage_data["has_coverage"]:
            try:
                # Try to get coverage data using coverage module
                result = subprocess.run(
                    ["python3", "-c", """
import coverage
import json
cov = coverage.Coverage()
cov.load()
data = cov.get_data()
files = data.measured_files()
coverage_info = {}
for f in files:
    try:
                        lines = cov.analysis2(f)
                        coverage_info[f] = {
                            'total_lines': len(lines[1]),
                            'covered_lines': len(lines[2]),
                            'coverage': len(lines[2]) / len(lines[1]) * 100 if lines[1] else 0
                        }
    except:
        pass
print(json.dumps(coverage_info))
"""],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                
                if result.returncode == 0:
                    coverage_info = json.loads(result.stdout)
                    coverage_data["coverage_by_module"] = coverage_info
                    
                    # Calculate overall coverage
                    total_lines = sum(info["total_lines"] for info in coverage_info.values())
                    covered_lines = sum(info["covered_lines"] for info in coverage_info.values())
                    coverage_data["coverage_percentage"] = covered_lines / total_lines * 100 if total_lines > 0 else 0
                    
                    # Categorize files
                    for file_path, info in coverage_info.items():
                        if info["coverage"] > 80:
                            coverage_data["covered_files"].append(file_path)
                        else:
                            coverage_data["uncovered_files"].append(file_path)
                            
            except Exception as e:
                print(f"Error analyzing coverage: {e}")
        
        return coverage_data
    
    def run_test_suite(self, test_type: str = "all") -> Dict[str, Any]:
        """Run test suite and return results."""
        start_time = time.time()
        results = {
            "test_type": test_type,
            "start_time": start_time,
            "end_time": None,
            "duration": None,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "output": "",
            "success": False
        }
        
        try:
            # Build test command
            cmd = ["python3", "-m", "pytest"]
            
            if test_type == "unit":
                cmd.extend(["-m", "unit", "tests/unit/"])
            elif test_type == "hardware":
                cmd.extend(["-m", "hardware", "tests/hardware/"])
            elif test_type == "integration":
                cmd.extend(["-m", "integration", "tests/integration/"])
            elif test_type == "quick":
                cmd.extend(["-m", "not slow and not gpu_intensive", "tests/"])
            else:
                cmd.append("tests/")
            
            cmd.extend(["-v", "--tb=short"])
            
            # Run tests
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            results["end_time"] = time.time()
            results["duration"] = results["end_time"] - results["start_time"]
            results["output"] = result.stdout + result.stderr
            
            # Parse results
            if result.returncode == 0:
                results["success"] = True
                # Simple parsing of pytest output
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'passed' in line:
                        results["passed"] = int(line.split('passed')[0].strip().split()[-1])
                    if 'failed' in line:
                        results["failed"] = int(line.split('failed')[0].strip().split()[-1])
                    if 'skipped' in line:
                        results["skipped"] = int(line.split('skipped')[0].strip().split()[-1])
            
        except Exception as e:
            results["output"] = f"Error running tests: {e}"
            results["end_time"] = time.time()
            results["duration"] = results["end_time"] - results["start_time"]
        
        return results
    
    def generate_coverage_charts(self) -> Dict[str, str]:
        """Generate coverage visualization charts."""
        charts = {}
        
        if not plt or not sns:
            return charts
        
        try:
            coverage_data = self.analyze_coverage()
            
            if coverage_data["has_coverage"]:
                # Create coverage pie chart
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Coverage by module
                modules = list(coverage_data["coverage_by_module"].keys())
                coverage_percentages = [coverage_data["coverage_by_module"][m]["coverage"] for m in modules]
                
                # Create bar chart
                bars = ax.bar(range(len(modules)), coverage_percentages)
                ax.set_xlabel('Modules')
                ax.set_ylabel('Coverage %')
                ax.set_title('Test Coverage by Module')
                ax.set_xticks(range(len(modules)))
                ax.set_xticklabels([m.split('/')[-1] for m in modules], rotation=45)
                
                # Color bars based on coverage
                for i, (bar, coverage) in enumerate(zip(bars, coverage_percentages)):
                    if coverage >= 80:
                        bar.set_color('green')
                    elif coverage >= 60:
                        bar.set_color('yellow')
                    else:
                        bar.set_color('red')
                
                plt.tight_layout()
                chart_path = self.project_root / "test_visualization_coverage.png"
                plt.savefig(chart_path)
                plt.close()
                
                charts["coverage_bar"] = str(chart_path)
                
                # Create test structure pie chart
                structure = self.analyze_test_structure()
                fig, ax = plt.subplots(figsize=(10, 6))
                
                categories = list(structure["test_categories"].keys())
                counts = [structure["test_categories"][cat]["count"] for cat in categories]
                
                ax.pie(counts, labels=categories, autopct='%1.1f%%', startangle=90)
                ax.set_title('Test Distribution by Category')
                
                chart_path = self.project_root / "test_visualization_distribution.png"
                plt.savefig(chart_path)
                plt.close()
                
                charts["distribution_pie"] = str(chart_path)
                
        except Exception as e:
            print(f"Error generating charts: {e}")
        
        return charts
    
    def create_html_report(self) -> str:
        """Create a comprehensive HTML report."""
        structure = self.analyze_test_structure()
        coverage_data = self.analyze_coverage()
        charts = self.generate_coverage_charts()
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>PersonalParakeet Test Visualization Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e9ecef; border-radius: 5px; }}
        .test-category {{ margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-left: 4px solid #007bff; }}
        .coverage-good {{ color: green; }}
        .coverage-warning {{ color: orange; }}
        .coverage-poor {{ color: red; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        img {{ max-width: 100%; height: auto; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PersonalParakeet Test Visualization Report</h1>
        <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>Test Structure Overview</h2>
        <div class="metric">
            <h3>Total Tests</h3>
            <p>{structure['total_tests']}</p>
        </div>
        <div class="metric">
            <h3>Test Files</h3>
            <p>{len(structure['test_files'])}</p>
        </div>
        <div class="metric">
            <h3>Test Categories</h3>
            <p>{len(structure['test_categories'])}</p>
        </div>
    </div>
    
    <div class="section">
        <h2>Test Categories</h2>
        {self._generate_category_html(structure['test_categories'])}
    </div>
    
    <div class="section">
        <h2>Test Coverage</h2>
        <div class="metric">
            <h3>Coverage Status</h3>
            <p class="{'coverage-good' if coverage_data['coverage_percentage'] > 80 else 'coverage-warning' if coverage_data['coverage_percentage'] > 60 else 'coverage-poor'}">
                {coverage_data['coverage_percentage']:.1f}%
            </p>
        </div>
        <div class="metric">
            <h3>Covered Files</h3>
            <p>{len(coverage_data['covered_files'])}</p>
        </div>
        <div class="metric">
            <h3>Uncovered Files</h3>
            <p>{len(coverage_data['uncovered_files'])}</p>
        </div>
        
        {self._generate_coverage_html(coverage_data)}
    </div>
    
    <div class="section">
        <h2>Visualizations</h2>
        {self._generate_charts_html(charts)}
    </div>
    
    <div class="section">
        <h2>Test Structure Tree</h2>
        {self._generate_tree_html(structure['structure_tree'])}
    </div>
</body>
</html>
"""
        
        report_path = self.project_root / "test_visualization_report.html"
        with open(report_path, 'w') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def _generate_category_html(self, categories: Dict[str, Any]) -> str:
        """Generate HTML for test categories."""
        html = ""
        for category, data in categories.items():
            html += f"""
            <div class="test-category">
                <h3>{category.title()}</h3>
                <p>Files: {len(data['files'])}</p>
                <p>Tests: {data['count']}</p>
                <p>Paths: {', '.join(data['paths'])}</p>
            </div>
            """
        return html
    
    def _generate_coverage_html(self, coverage_data: Dict[str, Any]) -> str:
        """Generate HTML for coverage data."""
        if not coverage_data["has_coverage"]:
            return "<p>No coverage data available</p>"
        
        html = "<h3>Coverage by Module</h3>"
        html += "<table>"
        html += "<tr><th>Module</th><th>Coverage %</th><th>Status</th></tr>"
        
        for module, info in coverage_data["coverage_by_module"].items():
            status_class = "coverage-good" if info["coverage"] > 80 else "coverage-warning" if info["coverage"] > 60 else "coverage-poor"
            html += f"""
            <tr>
                <td>{module.split('/')[-1]}</td>
                <td class="{status_class}">{info['coverage']:.1f}%</td>
                <td>{info['covered_lines']}/{info['total_lines']} lines</td>
            </tr>
            """
        
        html += "</table>"
        return html
    
    def _generate_charts_html(self, charts: Dict[str, str]) -> str:
        """Generate HTML for charts."""
        html = ""
        for chart_name, chart_path in charts.items():
            if os.path.exists(chart_path):
                relative_path = os.path.relpath(chart_path, self.project_root)
                html += f'<h3>{chart_name.replace("_", " ").title()}</h3>'
                html += f'<img src="{relative_path}" alt="{chart_name}">'
        return html
    
    def _generate_tree_html(self, tree: Dict[str, Any], level: int = 0) -> str:
        """Generate HTML for structure tree."""
        html = "<ul>"
        for child in tree.get("children", []):
            html += "<li>"
            html += f"<strong>{child['name']}</strong>"
            if child.get("count"):
                html += f" ({child['count']} files)"
            if child.get("children"):
                html += self._generate_tree_html(child, level + 1)
            html += "</li>"
        html += "</ul>"
        return html
    
    def run_interactive_dashboard(self):
        """Run the interactive dashboard (requires flet)."""
        if not ft:
            print("Flet not available. Run: pip install flet")
            return
        
        def main(page: ft.Page):
            page.title = "PersonalParakeet Test Visualization Dashboard"
            page.theme_mode = ft.ThemeMode.LIGHT
            page.scroll = ft.ScrollMode.AUTO
            
            # Header
            header = ft.Container(
                content=ft.Column([
                    ft.Text("PersonalParakeet Test Visualization Dashboard", size=24, weight=ft.FontWeight.BOLD),
                    ft.Text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", size=14)
                ]),
                padding=20,
                bgcolor=ft.colors.BLUE_50,
                border_radius=10
            )
            
            # Test structure section
            structure = self.analyze_test_structure()
            structure_section = ft.Container(
                content=ft.Column([
                    ft.Text("Test Structure Overview", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Total Tests", size=14),
                                ft.Text(str(structure['total_tests']), size=20, weight=ft.FontWeight.BOLD)
                            ]),
                            padding=10,
                            bgcolor=ft.colors.GREEN_50,
                            border_radius=5
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Test Files", size=14),
                                ft.Text(str(len(structure['test_files'])), size=20, weight=ft.FontWeight.BOLD)
                            ]),
                            padding=10,
                            bgcolor=ft.colors.BLUE_50,
                            border_radius=5
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Categories", size=14),
                                ft.Text(str(len(structure['test_categories'])), size=20, weight=ft.FontWeight.BOLD)
                            ]),
                            padding=10,
                            bgcolor=ft.colors.ORANGE_50,
                            border_radius=5
                        )
                    ])
                ]),
                padding=15,
                border_radius=10,
                border=ft.border.all(1, ft.colors.OUTLINE)
            )
            
            # Coverage section
            coverage_data = self.analyze_coverage()
            coverage_section = ft.Container(
                content=ft.Column([
                    ft.Text("Test Coverage", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Coverage", size=14),
                                ft.Text(f"{coverage_data['coverage_percentage']:.1f}%", size=20, weight=ft.FontWeight.BOLD,
                                       color=ft.colors.GREEN if coverage_data['coverage_percentage'] > 80 else ft.colors.ORANGE if coverage_data['coverage_percentage'] > 60 else ft.colors.RED)
                            ]),
                            padding=10,
                            bgcolor=ft.colors.GREEN_50 if coverage_data['coverage_percentage'] > 80 else ft.colors.ORANGE_50 if coverage_data['coverage_percentage'] > 60 else ft.colors.RED_50,
                            border_radius=5
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Covered Files", size=14),
                                ft.Text(str(len(coverage_data['covered_files'])), size=20, weight=ft.FontWeight.BOLD)
                            ]),
                            padding=10,
                            bgcolor=ft.colors.BLUE_50,
                            border_radius=5
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Uncovered Files", size=14),
                                ft.Text(str(len(coverage_data['uncovered_files'])), size=20, weight=ft.FontWeight.BOLD)
                            ]),
                            padding=10,
                            bgcolor=ft.colors.RED_50,
                            border_radius=5
                        )
                    ])
                ]),
                padding=15,
                border_radius=10,
                border=ft.border.all(1, ft.colors.OUTLINE)
            )
            
            # Test execution section
            execution_output = ft.Text("", size=12, selectable=True)
            execution_status = ft.Text("Ready", size=14, weight=ft.FontWeight.BOLD)
            
            def run_tests(e):
                execution_status.value = "Running tests..."
                execution_output.value = ""
                page.update()
                
                def run_in_thread():
                    try:
                        results = self.run_test_suite("all")
                        page.update()
                        
                        execution_status.value = f"Tests completed - {'✓' if results['success'] else '✗'}"
                        execution_output.value = results['output']
                        execution_status.color = ft.colors.GREEN if results['success'] else ft.colors.RED
                    except Exception as e:
                        execution_status.value = f"Error: {e}"
                        execution_output.value = str(e)
                        execution_status.color = ft.colors.RED
                    page.update()
                
                threading.Thread(target=run_in_thread, daemon=True).start()
            
            def generate_report(e):
                try:
                    report_path = self.create_html_report()
                    execution_status.value = f"Report generated: {report_path}"
                    execution_status.color = ft.colors.GREEN
                except Exception as e:
                    execution_status.value = f"Error generating report: {e}"
                    execution_status.color = ft.colors.RED
                page.update()
            
            execution_section = ft.Container(
                content=ft.Column([
                    ft.Text("Test Execution", size=18, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton("Run All Tests", on_click=run_tests),
                        ft.ElevatedButton("Generate Report", on_click=generate_report),
                        execution_status
                    ]),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Output:", size=14, weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=execution_output,
                                padding=10,
                                bgcolor=ft.colors.GREY_100,
                                border_radius=5,
                                height=200,
                                width=800
                            )
                        ])
                    )
                ]),
                padding=15,
                border_radius=10,
                border=ft.border.all(1, ft.colors.OUTLINE)
            )
            
            # Add all sections to page
            page.add(
                header,
                structure_section,
                coverage_section,
                execution_section
            )
        
        ft.app(target=main)
    
    def generate_json_report(self) -> str:
        """Generate a JSON report with all test data."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "test_structure": self.analyze_test_structure(),
            "coverage_data": self.analyze_coverage(),
            "test_results": self.test_results
        }
        
        report_path = self.project_root / "test_visualization_data.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(report_path)

def main():
    """Main function to run the test visualization dashboard."""
    dashboard = TestVisualizationDashboard()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--html":
            report_path = dashboard.create_html_report()
            print(f"HTML report generated: {report_path}")
        elif sys.argv[1] == "--json":
            report_path = dashboard.generate_json_report()
            print(f"JSON report generated: {report_path}")
        elif sys.argv[1] == "--charts":
            charts = dashboard.generate_coverage_charts()
            print(f"Charts generated: {list(charts.keys())}")
        else:
            print("Usage: python3 test_visualization_dashboard.py [--html|--json|--charts|--interactive]")
    else:
        print("Starting interactive dashboard...")
        dashboard.run_interactive_dashboard()

if __name__ == "__main__":
    main()