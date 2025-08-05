#!/usr/bin/env python3
"""
Script to clean up old test reports, keeping only the most recent 10 reports.
"""
import os
import glob
from pathlib import Path

def cleanup_test_reports():
    """Clean up old test reports, keeping only the most recent 10."""
    
    # Get project root
    project_root = Path(__file__).parent.parent
    reports_dir = project_root / "test_reports"
    archive_dir = reports_dir / "archive"
    
    if not reports_dir.exists():
        print("No test_reports directory found")
        return
    
    # Create archive directory if it doesn't exist
    archive_dir.mkdir(exist_ok=True)
    
    # Find all test report files
    report_files = list(reports_dir.glob("test_report_*.json")) + list(reports_dir.glob("test_report_*.txt"))
    
    # Sort by modification time (newest first)
    report_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Keep the most recent 10 files, archive the rest
    keep_count = 10
    files_to_archive = report_files[keep_count:]
    
    print(f"Found {len(report_files)} test report files")
    print(f"Keeping {min(keep_count, len(report_files))} most recent files")
    print(f"Archiving {len(files_to_archive)} old files")
    
    for file_path in files_to_archive:
        try:
            file_path.rename(archive_dir / file_path.name)
            print(f"Archived: {file_path.name}")
        except Exception as e:
            print(f"Error archiving {file_path.name}: {e}")
    
    print(f"Cleanup complete. {len(files_to_archive)} files archived.")

if __name__ == "__main__":
    cleanup_test_reports()