#!/usr/bin/env python3
"""
DictationView - Legacy Floating UI for PersonalParakeet v3
NOTE: This file contains the legacy Flet implementation that has been replaced
by the Rust+EGUI UI in src/gui.rs. This file is kept for reference but is no longer active.
The current UI is implemented in Rust with EGUI and connected via PyO3 bridge.
"""

import logging
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

import flet as ft

from personalparakeet.core.thought_linker import LinkingDecision

logger = logging.getLogger(__name__)


@dataclass
class DebugWidgetInfo:
    """Structured container for widget debug information."""
    name: str
    widget: ft.Control
    visible: bool = True
    opacity: float = 1.0
    last_update: float = 0.0
    update_count: int = 0


class DictationView:
    """
    Manages the floating dictation UI, its state, and debugging overlays.
    
    This class is designed to be a view component within a larger application.
    It handles rendering the UI, updating it based on application state,
    and providing extensive, optional debugging tools.
    """
    
    # Constants
    DEBUG_COLORS = [
        ft.Colors.RED_300, ft.Colors.BLUE_300, ft.Colors.GREEN_300,
        ft.Colors.YELLOW_300, ft.Colors.PURPLE_300, ft.Colors.ORANGE_300,
    ]
    SLOW_UPDATE_THRESHOLD = 0.1  # 100ms threshold
    
    def __init__(self, config: Any, profile_manager: Any):
        """Initializes the DictationView."""
        # Core dependencies
        self.config = config
        self.profile_manager = profile_manager
        
        # UI Components
        self.page: Optional[ft.Page] = None
        self.main_content: Optional[ft.Column] = None
        self.status_text: Optional[ft.Text] = None
        self.recognized_text: Optional[ft.Text] = None
        self.settings_button: Optional[ft.IconButton] = None
        self.settings_dialog: Optional[ft.AlertDialog] = None
        self.status_container: Optional[ft.Container] = None
        self.text_container: Optional[ft.Container] = None
        
        # State management
        self.is_recording: bool = False
        
        # Debug & Performance tracking
        self.debug_mode: bool = False
        self.debug_widgets: Dict[str, DebugWidgetInfo] = {}
        self.debug_info_panel: Optional[ft.Container] = None
        self.debug_toggle_button: Optional[ft.IconButton] = None
        self.performance_log: List[Dict[str, Any]] = []
        self.widget_update_times: Dict[str, float] = {}
        self.visibility_issues: List[str] = []
        self.last_update_time: float = 0.0
        self.update_count: int = 0
        self.error_count: int = 0
        self.last_error_time: float = 0.0
        self._debug_color_index: int = 0

    async def initialize(self, page: ft.Page):
        """
        Initializes and builds the UI. This should be called once by the main app.
        """
        self.page = page
        await self._configure_window()
        self._create_ui_components()
        self._setup_debug_controls()
        
        self.main_content = self._create_main_layout()
        self.page.add(self.main_content)
        await self._register_debug_widgets()
        self.page.update()
        logger.info("DictationView UI initialized successfully.")

    async def _configure_window(self):
        """Configures the main window properties."""
        if not self.page:
            return
        self.page.title = "PersonalParakeet v3"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_width = 900
        self.page.window_height = 800
        self.page.window_always_on_top = False
        self.page.window_opacity = 1.0
        self.page.window_resizable = True
        self.page.bgcolor = None  # Use default theme background
        logger.info("Window configured with standard visible settings.")

    def _create_ui_components(self):
        """Creates the primary UI widgets."""
        self.status_text = ft.Text("Ready", size=14, weight=ft.FontWeight.BOLD)
        self.recognized_text = ft.Text("", size=16, max_lines=10)
        self.settings_button = ft.IconButton(
            icon=ft.Icons.SETTINGS, on_click=self.open_settings_dialog
        )
        logger.info("UI components created.")

    def _setup_debug_controls(self):
        """Creates widgets used exclusively for debugging."""
        self.debug_info_panel = ft.Container(
            content=ft.Column(), bgcolor=ft.Colors.BLACK54, padding=10, visible=False
        )
        self.debug_toggle_button = ft.IconButton(
            icon=ft.Icons.BUG_REPORT,
            icon_color=ft.Colors.YELLOW,
            tooltip="Toggle Debug Mode",
            on_click=self._toggle_debug_mode,
        )
        logger.info("Debug controls created.")

    def _create_main_layout(self) -> ft.Column:
        """Assembles the main UI layout from components."""
        status_row_controls = [
            self.status_text,
            ft.Container(expand=True),  # Spacer
            self.settings_button,
            self.debug_toggle_button,
        ]
        
        self.status_container = ft.Container(
            content=ft.Row(status_row_controls),
            padding=10,
        )
        self.text_container = ft.Container(
            content=self.recognized_text, padding=10, expand=True
        )
        
        layout_controls = [
            self.status_container,
            ft.Divider(height=2, color=ft.Colors.YELLOW),
            self.text_container,
            self.debug_info_panel,
        ]
        # Filter out any None values to prevent errors
        return ft.Column([c for c in layout_controls if c], expand=True)

    def _get_next_debug_color(self) -> str:
        """Cycles through a list of predefined debug colors."""
        color = self.DEBUG_COLORS[self._debug_color_index % len(self.DEBUG_COLORS)]
        self._debug_color_index += 1
        return color

    async def _register_debug_widgets(self):
        """Populates the debug registry with key UI widgets for monitoring."""
        if not self.status_text or not self.recognized_text or not self.settings_button:
            return
        
        widgets_to_register = {
            "status_text": self.status_text,
            "recognized_text": self.recognized_text,
            "settings_button": self.settings_button,
        }
        for name, widget in widgets_to_register.items():
            self.debug_widgets[name] = DebugWidgetInfo(
                name=name, widget=widget, visible=widget.visible, opacity=widget.opacity or 1.0
            )
        logger.info(f"Registered {len(self.debug_widgets)} widgets for debugging.")

    async def _toggle_debug_mode(self, e: ft.ControlEvent):
        """Toggles debug mode on/off and updates UI visibility."""
        self.debug_mode = not self.debug_mode
        logger.info(f"Debug mode toggled: {self.debug_mode}")
        
        if self.debug_info_panel:
            self.debug_info_panel.visible = self.debug_mode
            if self.debug_mode:
                await self._refresh_debug_info()
        
        # Update container backgrounds
        debug_color = self._get_next_debug_color()
        if self.status_container:
            self.status_container.bgcolor = debug_color if self.debug_mode else None
        if self.text_container:
            self.text_container.bgcolor = self._get_next_debug_color() if self.debug_mode else None
        
        self.page.update()


    async def _refresh_debug_info(self):
        """Refreshes the content of the debug information panel."""
        if not self.debug_mode or not self.debug_info_panel:
            return
        
        total_time = sum(self.widget_update_times.values())
        avg_time = total_time / len(self.widget_update_times) if self.widget_update_times else 0
        slow_updates = sum(1 for t in self.widget_update_times.values() if t > self.SLOW_UPDATE_THRESHOLD)
        
        debug_content = [
            ft.Text("Debug Info", weight=ft.FontWeight.BOLD),
            ft.Text(f"UI Updates: {self.update_count}"),
            ft.Text(f"Errors: {self.error_count}"),
            ft.Text(f"Avg Update Time: {avg_time:.3f}s"),
            ft.Text(f"Slow Updates (> {self.SLOW_UPDATE_THRESHOLD}s): {slow_updates}"),
            ft.Divider(),
            ft.Text("Widget Status:", weight=ft.FontWeight.BOLD),
        ]
        for name, info in self.debug_widgets.items():
            status = "VISIBLE" if info.visible and info.opacity > 0 else "HIDDEN"
            debug_content.append(ft.Text(f"  {name}: {status} (Updates: {info.update_count})"))
        
        self.debug_info_panel.content = ft.Column(debug_content)

    async def _log_update(self, widget_name: str):
        """Internal helper to log performance and update debug info."""
        now = time.time()
        if self.last_update_time > 0:
            duration = now - self.last_update_time
            self.widget_update_times[f"{widget_name}_{self.update_count}"] = duration
        self.last_update_time = now
        self.update_count += 1
        
        if widget_name in self.debug_widgets:
            self.debug_widgets[widget_name].update_count += 1
        
        if self.debug_mode:
            await self._refresh_debug_info()


    async def open_settings_dialog(self, e: ft.ControlEvent):
        """Builds and displays the settings modal dialog."""
        if not self.page:
            return
        try:
            self.settings_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Settings"),
                content=self._build_settings_content(),
                actions=[ft.TextButton("Close", on_click=self._close_settings_dialog)],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            self.page.dialog = self.settings_dialog
            self.settings_dialog.open = True
            self.page.update()
        except Exception as e:
            logger.error(f"Failed to open settings dialog: {e}", exc_info=True)
            await self.show_error("Could not open settings.")

    def _build_settings_content(self) -> ft.Column:
        """Constructs the content for the settings dialog."""
        return ft.Column([
            ft.Switch(
                label="Enable Thought Linking",
                value=self.config.thought_linking.enabled,
                on_change=self._toggle_thought_linking,
            ),
            ft.Slider(
                min=0.5, max=5.0, divisions=9,
                value=self.config.vad.pause_threshold,
                label="VAD Pause Threshold: {value}s",
                on_change=self._update_vad_threshold,
            ),
        ])

    async def _toggle_thought_linking(self, e: ft.ControlEvent):
        """Callback for the thought linking switch."""
        self.config.thought_linking.enabled = e.data == "true"
        self.config.save_to_file()
        logger.info(f"Thought linking set to: {self.config.thought_linking.enabled}")

    async def _update_vad_threshold(self, e: ft.ControlEvent):
        """Callback for the VAD threshold slider."""
        self.config.vad.pause_threshold = float(e.data)
        self.config.save_to_file()
        logger.info(f"VAD threshold set to: {self.config.vad.pause_threshold}")

    async def _close_settings_dialog(self, e: ft.ControlEvent):
        """Closes the settings dialog."""
        if self.settings_dialog:
            self.settings_dialog.open = False
            self.page.update()

    # --- Public API Methods ---
    
    async def update_status(self, status: str, color: str = ft.Colors.WHITE):
        """Updates the status text display."""
        if not self.status_text or not self.page:
            return
        try:
            self.status_text.value = status
            self.status_text.color = color
            await self._log_update("status_text")
            self.page.update()
        except Exception as e:
            logger.error(f"Failed to update status: {e}", exc_info=True)
            self.error_count += 1
            
    async def update_text(self, text: str, decision: LinkingDecision = LinkingDecision.APPEND_WITH_SPACE):
        """Updates the recognized text display with appropriate color coding."""
        if not self.recognized_text or not self.page:
            return
        try:
            color_map = {
                LinkingDecision.START_NEW_THOUGHT: ft.Colors.CYAN_300,
                LinkingDecision.START_NEW_PARAGRAPH: ft.Colors.YELLOW_300,
            }
            self.recognized_text.value = text
            self.recognized_text.color = color_map.get(decision, ft.Colors.WHITE)
            await self._log_update("recognized_text")
            self.page.update()
        except Exception as e:
            logger.error(f"Failed to update text: {e}", exc_info=True)
            self.error_count += 1
            
    async def set_recording(self, is_recording: bool):
        """Updates UI to reflect recording state."""
        self.is_recording = is_recording
        if is_recording:
            await self.update_status("Recording...", ft.Colors.RED_ACCENT_400)
        else:
            await self.update_status("Ready", ft.Colors.GREEN_ACCENT_400)
        
    async def show_error(self, error_message: str):
        """Displays an error message in the status area."""
        await self.update_status(f"Error: {error_message}", ft.Colors.ORANGE_ACCENT_400)
