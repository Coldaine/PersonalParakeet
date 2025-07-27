#!/usr/bin/env python3
"""
PersonalParakeet Project Structure Cleanup Script
Cleans up root directory mess and organizes files properly
"""

import os
import shutil
from pathlib import Path
import json
from datetime import datetime

def create_cleanup_inventory():
    """Create an inventory of what we're about to move/delete"""
    inventory = {
        "cleanup_date": datetime.now().isoformat(),
        "actions": {
            "deleted": [],
            "moved": [],
            "archived": []
        }
    }
    return inventory

def safe_delete(file_path, inventory):
    """Safely delete a file and log it"""
    if os.path.exists(file_path):
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
            inventory["actions"]["deleted"].append(str(file_path))
            print(f"✅ Deleted: {file_path}")
        except Exception as e:
            print(f"❌ Failed to delete {file_path}: {e}")

def safe_move(src, dst, inventory, create_dirs=True):
    """Safely move a file and log it"""
    if os.path.exists(src):
        try:
            if create_dirs:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            inventory["actions"]["moved"].append(f"{src} -> {dst}")
            print(f"📁 Moved: {src} -> {dst}")
        except Exception as e:
            print(f"❌ Failed to move {src} to {dst}: {e}")

def main():
    """Main cleanup function"""
    print("🧹 PersonalParakeet Project Structure Cleanup")
    print("=" * 50)
    
    # Create inventory
    inventory = create_cleanup_inventory()
    
    # Create necessary directories
    os.makedirs("archive/v2-launchers", exist_ok=True)
    os.makedirs("archive/failed-experiments", exist_ok=True)
    os.makedirs("scripts", exist_ok=True)
    os.makedirs("tests", exist_ok=True)  # Should already exist but ensure it
    
    print("\n🗑️  DELETING GENUINE WASTE")
    print("-" * 30)
    
    # Delete genuine waste - no functional value
    waste_files = [
        "python-3.11.9-amd64.exe",      # 94MB space waste
        "organize_for_v3.py",            # Failed reorganization script
        "nul",                           # Corrupt/empty file
        "config_sample.json",            # Just an example file
        "command_mode_test_results.json", # Old test output
        "pyproject.toml",                # Conflicts with working system
    ]
    
    for file in waste_files:
        safe_delete(file, inventory)
    
    # Delete failed workshop experiments
    workshop_files = [
        "workshop_box_prototype.py",
        "workshop_box_fixed_transparency.py",
        "workshop_box_modern_mockup.html",
        "workshop_websocket_bridge_v2.py",
        "start_workshop_box.bat",
        "start_workshop_simple.py",
        "run_workshop.py",
        "tempreview/"  # Directory
    ]
    
    for file in workshop_files:
        safe_delete(file, inventory)
    
    print("\n📦 ARCHIVING V2 LAUNCHERS")
    print("-" * 30)
    
    # Archive all v2 launchers
    v2_launchers = [
        "start_dictation_view.py",
        "start_dictation_view_debug.py",
        "start_backend_only.py",
        "start_integrated.py",
        "run_tauri_directly.bat",
        "install_ui_deps.py",
    ]
    
    for launcher in v2_launchers:
        if os.path.exists(launcher):
            safe_move(launcher, f"archive/v2-launchers/{launcher}", inventory)
    
    print("\n📋 MOVING TEST SCRIPTS TO tests/")
    print("-" * 30)
    
    # Move all test scripts scattered in root
    test_scripts = [
        "demo_application_detection.py",
        "test_application_detection.py",
        "test_audio_flow.py",
        "test_backend_only.py",
        "test_clarity_engine_integration.py",
        "test_config_system.py",
        "test_enhanced_injection.py",
        "test_keyboard_hotkey.py",
        "test_rtx5090.py",
        "test_rtx5090_pytorch.py",
        "test_websocket_fixes.py",
        "run_all_tests.py",
        "run_tests.py"
    ]
    
    for test_file in test_scripts:
        if os.path.exists(test_file):
            safe_move(test_file, f"tests/{test_file}", inventory)
    
    print("\n🔧 MOVING UTILITY SCRIPTS TO scripts/")
    print("-" * 30)
    
    # Move utility scripts
    utility_scripts = [
        "config_tool.py",
        "fix_pytorch_cuda.bat",
        "fix_rtx5090_pytorch.bat",
    ]
    
    for script in utility_scripts:
        if os.path.exists(script):
            safe_move(script, f"scripts/{script}", inventory)
    
    print("\n📄 CREATING CLEANUP INVENTORY")
    print("-" * 30)
    
    # Save inventory
    with open("CLEANUP_INVENTORY.json", "w") as f:
        json.dump(inventory, f, indent=2)
    print("✅ Cleanup inventory saved to CLEANUP_INVENTORY.json")
    
    print("\n✨ CLEANUP COMPLETE!")
    print("=" * 50)
    print("Root directory should now only contain:")
    print("  - personalparakeet/ (v2 core)")
    print("  - v3-flet/ (v3 implementation)")
    print("  - tests/ (organized test suite)")
    print("  - scripts/ (utility scripts)")
    print("  - docs/ (documentation)")
    print("  - archive/ (archived code)")
    print("  - README.md, CLAUDE.md, requirements.txt")
    print("  - dictation_websocket_bridge.py (still used)")
    
    # Show final counts
    total_deleted = len(inventory["actions"]["deleted"])
    total_moved = len(inventory["actions"]["moved"])
    print(f"\n📊 Summary: {total_deleted} items deleted, {total_moved} items moved")

if __name__ == "__main__":
    main()