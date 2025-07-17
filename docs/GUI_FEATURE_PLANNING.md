# PersonalParakeet GUI - First Pass Feature List

This document outlines a comprehensive list of potential features for a Graphical User Interface (GUI) for PersonalParakeet, categorized for clarity and future development.

## I. Core Dictation & Control

1.  **Start/Stop/Pause Buttons:** Intuitive on-screen controls for dictation state.
2.  **Real-time Audio Level Meter:** Visual feedback on microphone input volume to help users adjust their microphone.
3.  **Dictation Status Indicator:** Clear visual cues (e.g., colored icon, text label) showing if dictation is active, paused, or stopped.
4.  **Microphone Selection:** A dropdown menu to easily select from available audio input devices.
5.  **Input Waveform/Spectrum Visualizer:** A real-time display of the audio input, helping users monitor clarity and noise.

## II. Configuration & Settings Management

1.  **Profile Management Interface:**
    *   **Profile Selector:** Dropdown or list to switch between pre-defined or custom dictation profiles (e.g., "Fast Conversation", "Accurate Document").
    *   **Profile Editor:** GUI elements (sliders, text boxes, checkboxes) to adjust profile parameters:
        *   Agreement Threshold (LocalAgreement).
        *   Chunk Duration.
        *   Max Pending Words.
        *   Word Timeout.
        *   Position Tolerance.
        *   Audio Level Threshold.
    *   **Profile Actions:** Buttons to create new profiles, duplicate, rename, and delete existing ones.
2.  **Injection Strategy Configuration:**
    *   **Strategy List:** Display all available injection strategies (UI Automation, XTEST, Clipboard, Basic Keyboard, etc.).
    *   **Enable/Disable Toggles:** Allow users to enable or disable specific strategies.
    *   **Strategy Reordering:** Drag-and-drop interface to customize the fallback order of injection strategies.
    *   **Strategy-Specific Settings:** Input fields or sliders for fine-tuning delays (e.g., `focus_acquisition_delay`, `clipboard_paste_delay`, `xdotool_timeout`) and retry attempts for each strategy.
3.  **Hotkey Customization:**
    *   **Hotkey Editor:** A user-friendly interface to assign and change hotkeys for dictation toggle, and potentially other commands. (e.g., "Press new hotkey" button).
4.  **Application-Specific Overrides:**
    *   Allow users to define custom injection strategy orders or delays for specific applications (e.g., "Always use Clipboard for VS Code").
    *   Interface to add/edit application detection patterns.

## III. Real-time Feedback & Debugging

1.  **Live Transcription Display:** A dedicated, scrollable text area within the GUI to show the transcribed text as it's processed, including pending words and committed text. This would replace the current console fallback.
2.  **Active Application Information:** Display the name, process name, window title, and classified type of the currently active application.
3.  **Injection Status Feedback:** Visual confirmation of which injection strategy was successfully used, or a clear message if all strategies failed.
4.  **Error & Warning Notifications:**
    *   Non-intrusive desktop notifications (pop-ups) for critical errors (e.g., "Microphone Disconnected", "GPU Out of Memory", "Text Injection Failed").
    *   A dedicated "Notifications" or "Alerts" section within the GUI.
5.  **Integrated Log Viewer:** A scrollable pane to display real-time application logs, with options to filter by log level (DEBUG, INFO, WARNING, ERROR) and search.
6.  **Open Log Directory Button:** A quick link to open the directory where log files are stored.

## IV. Advanced Dictation Features

1.  **Custom Vocabulary Management:**
    *   Interface to add, edit, and delete custom words or phrases.
    *   Import/export functionality for vocabulary lists.
2.  **Voice Commands/Macros:**
    *   Define custom voice commands (e.g., "new paragraph", "delete last word", "open browser", "type my email").
    *   Associate commands with actions (typing specific text, pressing key combinations, running external scripts/applications).
3.  **Correction & Editing Integration:**
    *   Basic in-app text editing capabilities (e.g., "correct that", "select last word").
    *   Integration with external text editors for more complex corrections.
4.  **Dictation History:**
    *   View a history of dictated text, possibly organized by session or date.
    *   Search and export past dictations.

## V. User Experience (UX) & System Integration

1.  **System Tray/Menubar Integration:**
    *   A small icon in the system tray (Windows) or menubar (Linux/macOS) for quick access to start/stop dictation, view status, and open settings.
    *   Context menu for common actions.
2.  **Theming & Customization:**
    *   Light/Dark mode toggle.
    *   Font size and style customization for the transcription display.
3.  **Onboarding & Help:**
    *   Interactive tooltips for complex settings.
    *   Integrated help documentation or links to online resources.
4.  **Auto-Start with OS:** Option to launch PersonalParakeet automatically when the operating system starts.
5.  **Start Minimized:** Option to start the application minimized to the system tray/menubar.
6.  **Update Mechanism:** Built-in functionality to check for, download, and install application updates.
