#!/usr/bin/env python3
"""
Headless UI component test for PersonalParakeet v3
Tests UI components without displaying window
"""

import asyncio
import flet as ft
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_ui_components(page: ft.Page):
    """Test UI components in headless mode"""
    
    results = {
        'page_created': False,
        'components_created': False,
        'events_working': False,
        'updates_working': False,
        'errors': []
    }
    
    try:
        # Test page configuration
        page.title = "PersonalParakeet v3 Test"
        page.window_width = 450
        page.window_height = 350
        results['page_created'] = True
        logger.info("✓ Page created and configured")
        
        # Test component creation
        components_tested = 0
        
        # Text component
        text = ft.Text("Test text", size=16)
        assert text.value == "Test text"
        components_tested += 1
        
        # Button component
        clicked = False
        def on_click(e):
            nonlocal clicked
            clicked = True
        
        button = ft.ElevatedButton("Test", on_click=on_click)
        components_tested += 1
        
        # Progress bar
        progress = ft.ProgressBar(value=0.5)
        assert progress.value == 0.5
        components_tested += 1
        
        # Container
        container = ft.Container(
            content=ft.Column([text, button, progress]),
            bgcolor=ft.Colors.BLACK,
            padding=20
        )
        components_tested += 1
        
        results['components_created'] = components_tested == 4
        logger.info(f"✓ Created {components_tested} components")
        
        # Add to page
        page.add(container)
        
        # Test updates
        text.value = "Updated text"
        progress.value = 0.75
        page.update()
        
        assert text.value == "Updated text"
        assert progress.value == 0.75
        results['updates_working'] = True
        logger.info("✓ Component updates working")
        
        # Test event handling (simulate click)
        if button.on_click:
            button.on_click(None)
            results['events_working'] = clicked
            logger.info(f"✓ Event handling: {'working' if clicked else 'failed'}")
        
    except Exception as e:
        results['errors'].append(str(e))
        logger.error(f"Error during test: {e}")
    
    # Print results
    print("\n" + "="*50)
    print("PersonalParakeet v3 UI Component Test Results")
    print("="*50)
    print(f"Page Creation:      {'✓ PASS' if results['page_created'] else '✗ FAIL'}")
    print(f"Component Creation: {'✓ PASS' if results['components_created'] else '✗ FAIL'}")
    print(f"Event Handling:     {'✓ PASS' if results['events_working'] else '✗ FAIL'}")
    print(f"Updates Working:    {'✓ PASS' if results['updates_working'] else '✗ FAIL'}")
    
    if results['errors']:
        print(f"\nErrors: {', '.join(results['errors'])}")
    else:
        print("\n✓ All UI components working correctly!")
    
    print("="*50)
    
    # Close the page to exit
    page.window_destroy()
    
    # Return success status
    all_passed = all([
        results['page_created'],
        results['components_created'],
        results['events_working'],
        results['updates_working']
    ])
    
    return 0 if all_passed else 1


def main():
    """Run headless UI test"""
    logger.info("Starting headless UI component test...")
    
    try:
        # Run in headless mode
        exit_code = asyncio.run(ft.app_async(
            target=test_ui_components,
            view=ft.FLET_APP_HIDDEN  # Hidden mode for testing
        ))
        
        sys.exit(exit_code or 0)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()