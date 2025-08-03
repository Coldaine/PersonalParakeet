#!/usr/bin/env python3
"""
PersonalParakeet Test Dashboard
A simple Flet dashboard for running manual tests

To run this dashboard:
1. First install flet: pip install flet
2. Then run: python test_dashboard.py

Or from v3-flet directory:
   poetry run python ../test_dashboard.py
"""

import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import threading

try:
    import flet as ft
except ImportError:
    print("Error: flet is not installed")
    print("Install it with: pip install flet")
    print("Or run from v3-flet directory: poetry run python ../test_dashboard.py")
    sys.exit(1)

class TestDashboard:
    def __init__(self):
        self.page = None
        self.output_text = None
        self.current_process = None
        self.root_dir = Path(__file__).parent
        self.v3_dir = self.root_dir / "v3-flet"
        
        # Define tests with descriptions
        self.tests = [
            {
                "name": "Live Audio Monitor",
                "script": "v3-flet/tests/utilities/test_live_audio.py",
                "description": "Monitor microphone levels in real-time. Speak or make noise to see audio levels.",
                "icon": ft.icons.MIC
            },
            {
                "name": "Full Pipeline Test",
                "script": "v3-flet/tests/utilities/test_full_pipeline.py",
                "description": "Test complete audio → STT → injection pipeline. Speak to test speech recognition.",
                "icon": ft.icons.RECORD_VOICE_OVER
            },
            {
                "name": "Microphone Test",
                "script": "v3-flet/tests/utilities/test_microphone.py",
                "description": "Basic microphone functionality test. Checks if microphone is accessible.",
                "icon": ft.icons.SETTINGS_VOICE
            },
            {
                "name": "Window Detection",
                "script": "v3-flet/tests/utilities/test_detector.py",
                "description": "Test window/application detection. Switch between windows to test detection.",
                "icon": ft.icons.WINDOW
            },
            {
                "name": "Text Injection",
                "script": "v3-flet/tests/utilities/test_injection.py",
                "description": "Test text injection. Position cursor in a text field before running.",
                "icon": ft.icons.KEYBOARD
            },
            {
                "name": "Enhanced Injection",
                "script": "v3-flet/tests/utilities/test_enhanced_injection.py",
                "description": "Test advanced injection strategies. Position cursor in target application.",
                "icon": ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT
            },
            {
                "name": "Quick Injection Test",
                "script": "v3-flet/quick_injection_test.py",
                "description": "Injects test text after 3-second delay. Position cursor where you want text.",
                "icon": ft.icons.TIMER
            }
        ]
    
    def run_test(self, test_script):
        """Run a test script in a subprocess"""
        def run_in_thread():
            try:
                # Check if test file exists
                test_path = self.root_dir / test_script
                if not test_path.exists():
                    self.output_text.value = f"❌ Test file not found: {test_script}\n"
                    self.page.update()
                    return
                
                # Update UI to show test is running
                self.output_text.value = f"Running {test_script}...\n"
                self.page.update()
                
                # Set up environment with v3-flet in PYTHONPATH
                env = os.environ.copy()
                env['PYTHONPATH'] = str(self.v3_dir) + os.pathsep + env.get('PYTHONPATH', '')
                
                # Determine if we should use poetry
                use_poetry = (self.v3_dir / "pyproject.toml").exists()
                
                if use_poetry:
                    # Run with poetry from v3-flet directory
                    cmd = ["poetry", "run", "python", str(test_path.absolute())]
                    cwd = self.v3_dir
                else:
                    # Run directly
                    cmd = [sys.executable, str(test_path)]
                    cwd = self.root_dir
                
                # Run the test
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    env=env,
                    cwd=cwd
                )
                self.current_process = process
                
                # Stream output
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.output_text.value += line
                        self.page.update()
                
                process.wait()
                self.current_process = None
                
                if process.returncode == 0:
                    self.output_text.value += "\n✅ Test completed successfully\n"
                else:
                    self.output_text.value += f"\n❌ Test failed with exit code {process.returncode}\n"
                self.page.update()
                
            except Exception as e:
                self.output_text.value += f"\n❌ Error running test: {str(e)}\n"
                self.page.update()
        
        # Run in thread to not block UI
        thread = threading.Thread(target=run_in_thread)
        thread.start()
    
    def stop_test(self, e):
        """Stop the currently running test"""
        if self.current_process:
            self.current_process.terminate()
            self.output_text.value += "\n⚠️ Test stopped by user\n"
            self.page.update()
    
    def clear_output(self, e):
        """Clear the output text"""
        self.output_text.value = ""
        self.page.update()
    
    def create_test_card(self, test):
        """Create a card for a test"""
        # Check if test file exists
        test_exists = (self.root_dir / test["script"]).exists()
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(test["icon"], size=30),
                        ft.Text(test["name"], size=20, weight=ft.FontWeight.BOLD)
                    ]),
                    ft.Text(test["description"], size=14),
                    ft.ElevatedButton(
                        "Run Test" if test_exists else "Test Not Found",
                        icon=ft.icons.PLAY_ARROW if test_exists else ft.icons.ERROR,
                        on_click=lambda e, script=test["script"]: self.run_test(script),
                        disabled=not test_exists
                    )
                ]),
                padding=20
            ),
            margin=10
        )
    
    def main(self, page: ft.Page):
        self.page = page
        page.title = "PersonalParakeet Test Dashboard"
        page.theme_mode = ft.ThemeMode.DARK
        page.window_width = 900
        page.window_height = 800
        
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Text("PersonalParakeet Test Dashboard", size=30, weight=ft.FontWeight.BOLD),
                ft.Text("Run manual tests with human-in-the-loop interaction", size=16),
                ft.Divider()
            ]),
            padding=20
        )
        
        # Test cards
        test_cards = ft.Column(
            [self.create_test_card(test) for test in self.tests],
            scroll=ft.ScrollMode.AUTO
        )
        
        # Output area
        self.output_text = ft.TextField(
            value="",
            multiline=True,
            min_lines=10,
            max_lines=20,
            read_only=True,
            color=ft.colors.GREEN_400,
            bgcolor=ft.colors.BLACK87,
            text_style=ft.TextStyle(font_family="Consolas, monospace")
        )
        
        output_section = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Output", size=20, weight=ft.FontWeight.BOLD),
                    ft.IconButton(
                        icon=ft.icons.STOP,
                        icon_color=ft.colors.RED,
                        tooltip="Stop running test",
                        on_click=self.stop_test
                    ),
                    ft.IconButton(
                        icon=ft.icons.CLEAR,
                        icon_color=ft.colors.BLUE,
                        tooltip="Clear output",
                        on_click=self.clear_output
                    )
                ]),
                self.output_text
            ]),
            padding=20
        )
        
        # Layout
        page.add(
            ft.Column([
                header,
                ft.Row([
                    ft.Container(
                        content=test_cards,
                        width=500,
                        height=400
                    ),
                    ft.VerticalDivider(),
                    ft.Container(
                        content=output_section,
                        expand=True
                    )
                ], expand=True)
            ])
        )
        
        # Instructions
        page.overlay.append(
            ft.Snackbar(
                content=ft.Text("👋 Welcome! Click 'Run Test' on any card to start testing."),
                open=True
            )
        )
        page.update()

if __name__ == "__main__":
    dashboard = TestDashboard()
    ft.app(target=dashboard.main)