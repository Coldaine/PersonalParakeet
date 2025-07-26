#!/usr/bin/env python3
"""
Fix for async/await issues in UI button handlers
Updates DictationView to use proper event loop handling
"""

import re

def fix_dictation_view():
    """Fix async issues in dictation_view.py"""
    
    # Read the file
    with open('ui/dictation_view.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Update the _on_clear_text method to be properly sync
    old_clear = """    def _on_clear_text(self):
        \"\"\"Handle clear text button (sync)\"\"\"
        asyncio.create_task(self._clear_current_text())"""
    
    new_clear = """    def _on_clear_text(self):
        \"\"\"Handle clear text button (sync)\"\"\"
        try:
            # Use the page's event loop if available
            if hasattr(self, 'page') and self.page:
                self.page.run_task(self._clear_current_text())
            else:
                # Fallback to direct update
                self.current_text = ""
                self.clarity_queue = []
                self.confidence = 0.0
                if self.text_display:
                    self.page.update()
        except Exception as e:
            logger.error(f"Error clearing text: {e}")"""
    
    content = content.replace(old_clear, new_clear)
    
    # Fix 2: Update _on_toggle_command_mode
    old_toggle = """    def _on_toggle_command_mode(self):
        \"\"\"Handle command mode toggle button (sync)\"\"\"
        self.command_mode_enabled = not self.command_mode_enabled
        self.audio_engine.set_command_mode_enabled(self.command_mode_enabled)
        asyncio.create_task(self._update_ui_state())
        logger.info(f"Command mode {'enabled' if self.command_mode_enabled else 'disabled'}")"""
    
    new_toggle = """    def _on_toggle_command_mode(self):
        \"\"\"Handle command mode toggle button (sync)\"\"\"
        self.command_mode_enabled = not self.command_mode_enabled
        self.audio_engine.set_command_mode_enabled(self.command_mode_enabled)
        try:
            if hasattr(self, 'page') and self.page:
                self.page.run_task(self._update_ui_state())
            else:
                # Direct update
                if self.control_panel:
                    self.control_panel.update_command_mode(self.command_mode_enabled)
                self.page.update()
        except Exception as e:
            logger.error(f"Error toggling command mode: {e}")
        logger.info(f"Command mode {'enabled' if self.command_mode_enabled else 'disabled'}")"""
    
    content = content.replace(old_toggle, new_toggle)
    
    # Fix 3: Update _on_commit_text to handle async properly
    content = re.sub(
        r'asyncio\.create_task\(self\._inject_text_async\((.*?)\)\)',
        r'self.page.run_task(self._inject_text_async(\1))',
        content
    )
    
    content = re.sub(
        r'asyncio\.create_task\(self\._clear_current_text\(\)\)',
        r'self.page.run_task(self._clear_current_text())',
        content
    )
    
    # Write back
    with open('ui/dictation_view.py', 'w') as f:
        f.write(content)
    
    print("Fixed async/await issues in dictation_view.py")


def add_run_task_to_page():
    """Add run_task helper to ft.Page if not present"""
    
    # This would need to be done in the main.py or as a monkey patch
    fix_code = '''
# Add this to main.py after page configuration:
def add_run_task_helper(page):
    """Add run_task helper to page for sync->async calls"""
    import asyncio
    
    def run_task(coro):
        """Run an async task in the page's event loop"""
        try:
            # Get the current event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Schedule the coroutine
                asyncio.create_task(coro)
            else:
                # If no loop, run it
                asyncio.run(coro)
        except RuntimeError:
            # No event loop, create one
            asyncio.run(coro)
    
    page.run_task = run_task
'''
    
    print("Add this helper function to main.py:")
    print(fix_code)


if __name__ == "__main__":
    fix_dictation_view()
    print("\nAlso need to add helper to main.py:")
    add_run_task_to_page()