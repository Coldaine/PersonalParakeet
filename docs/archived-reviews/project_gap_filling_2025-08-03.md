# Plan to Address Project Gaps

**Date**: 2025-08-03
**Author**: Gemini

This plan outlines the steps to address the key gaps identified in the `project_review_2025-08-03.md` file. The focus is on activating and enhancing existing features, improving context detection, and strengthening the testing suite.

---

#### 1. Activate and Enhance the Thought Linking System

**Objective**: Enable the currently disabled `ThoughtLinker` and provide it with the necessary data to function correctly.

**Tasks**:

1.  **Enable Thought Linking in Default Configuration**:
    *   Modify `src/personalparakeet/config.py` to set `thought_linking.enabled` to `True` by default.

2.  **Implement Context Detectors**:
    *   **`CursorDetector`**: Implement the platform-specific logic in `src/personalparakeet/core/cursor_detector.py` to get the current cursor position.
        *   **Windows**: Use `win32api.GetCursorPos`.
        *   **Linux**: Use `Xlib.display.Display().screen().root.query_pointer()`.
        *   **macOS**: Use `Quartz.CGEventGetLocation(Quartz.CGEventCreate(None))`.
    *   **`WindowDetector`**: Implement the platform-specific logic in `src/personalparakeet/core/window_detector.py` to get the active window's title and process name.
        *   **Windows**: Use `win32gui.GetForegroundWindow` and `win32process.GetWindowThreadProcessId`.
        *   **Linux**: Use `Xlib` to get the window title and process information.
        *   **macOS**: Use `AppKit.NSWorkspace` to get the active application's information.

3.  **Integrate Detectors with ThoughtLinker**:
    *   Ensure that the `ThoughtLinker` correctly initializes and uses the newly implemented detectors.

---

#### 2. Strengthen the Testing Suite

**Objective**: Add unit tests to complement the existing integration and hardware tests.

**Tasks**:

1.  **Add Unit Tests for `ThoughtLinker`**:
    *   Create `tests/unit/test_thought_linker.py`.
    *   Write tests for the `_make_decision_from_signals` method to verify that it correctly interprets different combinations of signals.
    *   Write tests for the `_calculate_text_similarity` method to ensure it produces reasonable similarity scores.

2.  **Add Unit Tests for `Config`**:
    *   Create `tests/unit/test_config.py`.
    *   Write tests for the configuration loading and saving logic.
    *   Add tests for the new validation logic (to be added in the next step).

---

#### 3. Improve Configuration Validation

**Objective**: Add explicit validation for configuration values.

**Tasks**:

1.  **Add a `validate` method to `V3Config`**:
    *   In `src/personalparakeet/config.py`, add a `validate` method to the `V3Config` class.
    *   This method should check that numeric values are within reasonable ranges (e.g., `sample_rate > 0`, `0.0 <= opacity <= 1.0`).
    *   The method should raise a `ValueError` if an invalid configuration is detected.

2.  **Call `validate` on Load**:
    *   Modify the `_load_from_file` method in `V3Config` to call the new `validate` method after loading the configuration data.

---

#### 4. Enhance the User Interface

**Objective**: Expose more of the application's features through the UI.

**Tasks**:

1.  **Add a Configuration Menu**:
    *   In `src/personalparakeet/ui/dictation_view.py`, add a settings icon or button.
    *   This button should open a new dialog or view that allows the user to:
        *   Switch between configuration profiles.
        *   Enable or disable the `ThoughtLinker`.
        *   Adjust key settings like the VAD pause threshold.

2.  **Provide Visual Feedback for Thought Linking**:
    *   Modify the `DictationView` to visually indicate the `ThoughtLinker`'s decisions. For example, display a small icon or change the color of the text to show whether the system is appending, starting a new paragraph, or starting a new thought.
