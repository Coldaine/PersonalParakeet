#!/usr/bin/env python3
"""
PersonalParakeet v3 File Organization Script
Safely archives v2 code while preparing clean v3 structure
"""

import os
import shutil
import json
from pathlib import Path

def create_archive_structure():
    """Create archive directory structure"""
    dirs = [
        'archive/v2-tauri',
        'archive/v2-experiments', 
        'archive/v2-tests',
        'docs/v3',
        'docs/v2',
        'v3/ui',
        'v3/core',
        'v3/assets'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created {dir_path}")

def archive_v2_files():
    """Archive all v2-specific files"""
    
    # Tauri/WebSocket files
    tauri_files = [
        'dictation-view-ui/',
        'dictation_websocket_bridge.py',
        'start_dictation_view.py', 
        'start_integrated.py',
        'start_dictation_view_debug.py',
        'start_backend_only.py',
        'test_backend_only.py',
        'run_tauri_directly.bat'
    ]
    
    # Failed experiments
    experiment_files = [
        'workshop_box_fixed_transparency.py',
        'workshop_box_prototype.py', 
        'workshop_box_modern_mockup.html',
        'workshop_websocket_bridge_v2.py',
        'run_workshop.py',
        'start_workshop_box.bat',
        'start_workshop_simple.py',
        'config_sample.json',
        'config_tool.py',
        'demo_application_detection.py',
        'install_ui_deps.py',
        'fix_pytorch_cuda.bat',
        'fix_rtx5090_pytorch.bat',
        'python-3.11.9-amd64.exe',
        'pyproject.toml',
        'tempreview/'
    ]
    
    # Scattered test files
    test_files = [
        'test_audio_flow.py',
        'test_clarity_engine_integration.py',
        'test_config_system.py', 
        'test_enhanced_injection.py',
        'test_keyboard_hotkey.py',
        'test_rtx5090.py',
        'test_rtx5090_pytorch.py',
        'test_websocket_fixes.py',
        'test_application_detection.py',
        'run_all_tests.py',
        'run_tests.py',
        'command_mode_test_results.json'
    ]
    
    def safe_move(src, dst_dir):
        """Safely move file/folder to destination"""
        if os.path.exists(src):
            dst = os.path.join(dst_dir, os.path.basename(src))
            if os.path.exists(dst):
                print(f"⚠️  {src} already exists in {dst_dir}")
                return
            try:
                shutil.move(src, dst)
                print(f"📦 Archived {src} → {dst_dir}")
            except Exception as e:
                print(f"❌ Failed to move {src}: {e}")
        else:
            print(f"⚠️  {src} not found")
    
    # Archive files
    print("\n=== Archiving Tauri/WebSocket Files ===")
    for f in tauri_files:
        safe_move(f, 'archive/v2-tauri')
        
    print("\n=== Archiving Experiments ===") 
    for f in experiment_files:
        safe_move(f, 'archive/v2-experiments')
        
    print("\n=== Archiving Test Files ===")
    for f in test_files:
        safe_move(f, 'archive/v2-tests')

def organize_docs():
    """Organize documentation into v2/v3 folders"""
    
    v3_docs = [
        'docs/Flet_Refactor_Implementation_Plan.md',
        'docs/Architecture_Decision_Record_Flet.md', 
        'docs/KNOWLEDGE_BASE.md',
        'docs/GEMINI_REORGANIZATION_PLAN.md',
        'docs/V3_PROVEN_CODE_LIBRARY.md'
    ]
    
    v2_docs = [
        'docs/PersonalParakeet_v2_Architectural_Brief.md',
        'docs/WORKSHOP_BOX_CRASH_FIXES.md',
        'docs/WORKSHOP_BOX_TROUBLESHOOTING.md',
        'docs/Workshop_Box_Adaptive_Sizing_Spec.md',
        'docs/Workshop_Box_Modern_Implementation_Plan.md',
        'docs/DICTATION_VIEW_SETUP_GUIDE.md',
        'docs/setup_workshop_box.md'
    ]
    
    def safe_move_doc(src, dst_dir):
        if os.path.exists(src):
            dst = os.path.join(dst_dir, os.path.basename(src))
            try:
                shutil.move(src, dst) 
                print(f"📄 Moved {os.path.basename(src)} → {dst_dir}")
            except Exception as e:
                print(f"❌ Failed to move doc {src}: {e}")
    
    print("\n=== Organizing Documentation ===")
    for doc in v3_docs:
        safe_move_doc(doc, 'docs/v3')
        
    for doc in v2_docs:
        safe_move_doc(doc, 'docs/v2')

def create_v3_placeholders():
    """Create placeholder files for v3 structure"""
    
    placeholders = {
        'v3/main.py': '''#!/usr/bin/env python3
"""
PersonalParakeet v3 - Flet Entry Point
Single-process dictation system with transparent floating UI
"""

import flet as ft
# Implementation coming from Gemini refactor

def main(page: ft.Page):
    # v3 Flet implementation
    pass

if __name__ == "__main__":
    ft.app(target=main)
''',
        'v3/audio_engine.py': '''"""
v3 Audio Engine - Producer-Consumer Pipeline
Ported from v2 WebSocket bridge with threading fixes
"""

import queue
import threading
import sounddevice as sd
# Implementation coming from Gemini refactor
''',
        'v3/requirements.txt': '''# PersonalParakeet v3 Dependencies
flet>=0.21.0
sounddevice>=0.4.6
numpy>=1.24.0
torch>=2.0.0
nemo_toolkit[asr]>=1.19.0
''',
        'v3/__init__.py': '# PersonalParakeet v3 Package',
        'v3/ui/__init__.py': '# v3 UI Components',
        'v3/core/__init__.py': '# v3 Core Components',
        'v3/assets/.gitkeep': '# Assets directory'
    }
    
    print("\n=== Creating v3 Placeholders ===")
    for file_path, content in placeholders.items():
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"📝 Created {file_path}")

def create_inventory():
    """Create inventory of what was moved where"""
    inventory = {
        "timestamp": "2025-07-21",
        "purpose": "Clean file organization before v3 Flet refactor",
        "archives_created": {
            "v2-tauri": "Tauri UI, WebSocket bridge, launcher scripts",
            "v2-experiments": "Workshop prototypes, config tools, debug utilities", 
            "v2-tests": "Scattered test files from root directory"
        },
        "docs_organized": {
            "v2": "All v2-specific documentation",
            "v3": "Flet refactor planning and implementation docs"
        },
        "v3_structure_created": "Clean directory structure with placeholders",
        "preserved_unchanged": [
            "personalparakeet/ - Core working algorithms (Clarity Engine, VAD, etc.)",
            "tests/ - Organized test suite with proven test patterns", 
            "docs/testing/ - Test documentation and validation",
            "requirements.txt - Current dependencies, will be updated for v3",
            "README.md - Project overview, updated for v3 status",
            "CLAUDE.md - Development guidance, already updated for v3"
        ],
        "ready_for_gemini": True,
        "rollback_possible": "All v2 code preserved in archive/ directories"
    }
    
    with open('REORGANIZATION_INVENTORY.json', 'w') as f:
        json.dump(inventory, f, indent=2)
    
    print("\n=== Reorganization Complete ===")
    print("📋 Created REORGANIZATION_INVENTORY.json")
    print("✅ v2 code safely archived")  
    print("🏗️  v3 structure ready")
    print("📚 Documentation organized")

def main():
    """Execute full reorganization"""
    print("🗂️  PersonalParakeet v3 File Organization")
    print("=" * 50)
    print("This will:")
    print("  • Archive all v2 Tauri/WebSocket code")
    print("  • Organize documentation into v2/v3 folders") 
    print("  • Create clean v3 structure for Flet refactor")
    print("  • Preserve all working core code unchanged")
    
    # Confirm action
    response = input("\nContinue with reorganization? (yes/no): ")
    if response.lower() != 'yes':
        print("Cancelled.")
        return
        
    create_archive_structure()
    archive_v2_files()
    organize_docs()  
    create_v3_placeholders()
    create_inventory()
    
    print("\n🎉 File organization complete!")
    print("   📦 v2 code safely archived")
    print("   🏗️  v3 clean structure created")
    print("   📚 Documentation organized")
    print("   ✅ Ready for Gemini refactor")
    print("\nNext step: Run Gemini reorganization to populate v3/ with working code")

if __name__ == "__main__":
    main()