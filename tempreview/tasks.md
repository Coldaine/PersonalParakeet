# Implementation Plan

## Overview
PersonalParakeet has a **PROVEN WORKING CORE SYSTEM** ✅. The main components (audio capture, Parakeet transcription, LocalAgreement buffering, F4 hotkey) are functional. This implementation plan focuses on fixing the remaining issues and enhancing the working system.

## Current Status Summary
- ✅ **Audio capture working** - Windows sounddevice integration functional
- ✅ **Parakeet transcription working** - NVIDIA model processing speech in real-time  
- ✅ **LocalAgreement buffering working** - Text stabilization preventing rewrites
- ✅ **F4 hotkey working** - Toggle functionality operational
- ✅ **Text output fixed** - Callback errors resolved with fallback mechanisms

## Priority Tasks (Fix Current Issues)

- [x] 1. Clean up workspace and consolidate working code ✅






  - ✅ Remove experimental and duplicate files (dictation_minimal.py, test_*.py, etc.)
  - ✅ Keep only essential working files (dictation_simple_fixed.py, ESSENTIAL_LocalAgreement_Code.py)
  - ✅ Archive or delete package_complete_documents folder (outdated documentation)
  - ✅ Clean up any other loose files not needed for current implementation
  - ✅ Remove redundant root entry point files (run_dictation.py, run_enhanced_dictation.py)
  - _Note: All files are preserved in git history if needed later_

- [x] 2. Fix text output callback system ✅
  - ✅ Debugged keyboard.write() callback errors in SimpleDictation.output_text()
  - ✅ Added thread safety detection and handling
  - ✅ Implemented fallback methods (press_and_release, console display)
  - ✅ Added error tracking and automatic fallback switching
  - _Requirements: 4.1, 4.6_
  - _Files: personalparakeet/dictation.py lines 46-96_

- [x] 3. Enhance error handling and robustness ✅
  - ✅ Added comprehensive exception handling for audio callback errors
  - ✅ Implemented graceful degradation with consecutive error tracking
  - ✅ Added fallback console display when keyboard injection fails
  - ✅ Enhanced GPU out-of-memory handling with cache clearing
  - ✅ Improved resource cleanup and thread management
  - _Requirements: 12.1, 12.4, 12.5_
  - _Files: personalparakeet/dictation.py process_audio_loop(), audio_callback(), main()_


- [x] 4. Polish the working system ✅

  - ✅ Add device selection capability to SimpleDictation
  - ✅ Implement proper cleanup on shutdown (Ctrl+C handling)
  - ✅ Add configuration options for agreement threshold and chunk duration
  - ✅ Clean up redundant root files and use proper package entry points
  - _Requirements: 1.4, 9.1, 3.6_

## Enhancement Tasks (Build on Working System)

- [ ] 5. Implement platform-aware intelligent text injection strategies
  - [ ] 4.1 Create platform detection system
    - Detect operating system (Windows, Linux, macOS)
    - Detect desktop environment (KDE, GNOME, Windows Desktop)
    - Detect session type (X11, Wayland)
    - Cache platform information for performance
    - _Requirements: 4.1_

  - [ ] 4.2 Create application detection system
    - Platform-specific active window detection
    - Windows: Win32 API for process/window info
    - Linux: xdotool/D-Bus for window detection
    - Classify applications (EDITOR, BROWSER, TERMINAL, UNKNOWN)
    - _Requirements: 4.2, 4.3, 4.4_

  - [ ] 4.3 Implement Windows text injection
    - Primary: UI Automation API for smart injection (most reliable)
      - Initialize IUIAutomation COM object
      - Get focused element via GetFocusedElement()
      - Try TextPattern for rich text controls
      - Try ValuePattern for simple text inputs
    - Secondary: keyboard.write() for direct injection
    - Tertiary: Win32 SendInput for complex scenarios
    - Clipboard: win32clipboard + Ctrl+V for editors
    - Fallback: Character-by-character typing
    - _Requirements: 4.5, 4.7_

  - [ ] 4.4 Implement Linux KDE text injection
    - Primary: XTEST via python-xlib for X11
    - Secondary: xdotool with --clearmodifiers
    - KDE apps: D-Bus integration (Konsole, Kate)
    - Clipboard: xclip for code editors
    - _Requirements: 4.5, 4.7_

  - [ ] 4.5 Implement Linux GNOME text injection
    - Primary: AT-SPI for Wayland compatibility
    - Secondary: XTEST for X11 sessions
    - IBus: Complex text input method
    - Fallback: xdotool or wtype
    - _Requirements: 4.5, 4.7_

  - [ ] 4.6 Add injection strategy selection
    - Auto-detect optimal method per platform/app
    - Code editors: Prefer clipboard paste
    - Browsers: Character-by-character typing
    - Terminals: Platform-specific APIs
    - Unknown apps: Conservative typing
    - _Requirements: 4.5, 4.7_

  - [ ] 4.7 Implement fallback strategies
    - Primary method failure detection
    - Automatic fallback to secondary methods
    - Last resort: Overlay display
    - Error logging and diagnostics
    - _Requirements: 4.6_

- [ ] 6. Add advanced Voice Activity Detection
  - [ ] 5.1 Create dual VAD system (Silero + WebRTC)
    - Implement SileroVAD integration for neural speech detection
    - Add WebRTCVAD for traditional energy-based detection
    - Create VADResult data structure with confidence scores
    - _Requirements: 7.1, 7.8_

  - [ ] 5.2 Implement VAD configuration and adaptation
    - Add configurable sensitivity thresholds (0.1-0.9 range)
    - Implement automatic noise floor adaptation
    - Create pre-roll and post-roll buffer configuration (0.5s/1.0s defaults)
    - _Requirements: 7.2, 7.3, 7.5, 7.6_

  - [ ] 5.3 Integrate VAD with audio processing pipeline
    - Add speech boundary detection for utterance processing
    - Implement low-power monitoring mode for silence periods
    - Create streaming chunk processing for long utterances (>15 seconds)
    - _Requirements: 7.4, 7.7, 7.9_

- [ ] 7. Implement dual GPU optimization
  - [ ] 6.1 Create GPU detection and allocation system
    - Detect available NVIDIA GPUs with memory information
    - Implement RTX 5090 + RTX 3090 allocation strategy
    - Add GPU memory monitoring and pressure handling
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ] 6.2 Add GPU resource management
    - Allocate Parakeet to primary GPU (RTX 5090)
    - Reserve secondary GPU for future LLM processing
    - Implement automatic fallback for single GPU systems
    - _Requirements: 6.4, 6.5, 6.6_

- [ ] 8. Add status display and user interface
  - [ ] 7.1 Create transparent overlay widget
    - Display dictation status (listening, processing, idle)
    - Show committed vs pending text with visual distinction
    - Add error messages and system notifications
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [ ] 7.2 Implement system tray integration
    - Add system tray icon with status indication
    - Create context menu for basic controls
    - Provide alternative to overlay for minimal UI preference
    - _Requirements: 10.7_

- [x] 9. Add configuration and customization system ✅
  - [x] 8.1 Implement TOML configuration loading ✅
    - ✅ Create configuration file structure with sensible defaults
    - ✅ Add audio device, model, and agreement threshold settings
    - ✅ Implement configuration validation and error reporting
    - _Requirements: 9.1, 9.2, 9.7_
    - _Files: personalparakeet/config.py - ConfigurationManager class_

  - [x] 8.2 Add hotkey and device configuration ✅
    - ✅ Allow custom hotkey bindings (alternative to F4)
    - ✅ Add audio device selection by name pattern
    - ✅ Implement VAD sensitivity and timing configuration
    - _Requirements: 9.4, 9.5_
    - _Files: personalparakeet/config.py - AudioConfig, HotkeyConfig_

  - [x] 8.3 Implement configuration profile system ✅
    - ✅ Create ConfigurationProfile dataclass with all tunable parameters:
      - Agreement threshold (1-5): Number of consecutive agreements before committing
      - Chunk duration (0.3-2.0s): Audio processing chunk size
      - Max pending words (5-30): Maximum words in pending buffer
      - Word timeout (2.0-7.0s): Time before forcing pending words to commit
      - Position tolerance (1-3): Word position flexibility for agreement matching
      - Audio level threshold (0.001-0.1): Minimum audio level to process
    - _Requirements: 15.1_
    - _Files: personalparakeet/config.py - ConfigurationProfile dataclass_

  - [x] 8.4 Create pre-defined configuration profiles ✅
    - ✅ Implement Fast Conversation Mode (threshold=1, chunk=0.3s, max_words=8, timeout=2.0s)
    - ✅ Implement Balanced Mode as default (threshold=2, chunk=1.0s, max_words=15, timeout=4.0s)
    - ✅ Implement Accurate Document Mode (threshold=3, chunk=2.0s, max_words=30, timeout=7.0s)
    - ✅ Implement Low-Latency Mode (threshold=1, chunk=0.5s, max_words=5, timeout=2.5s)
    - _Requirements: 15.2, 15.3, 15.4, 15.5, 15.6_
    - _Files: personalparakeet/config.py - FAST_CONVERSATION, BALANCED_MODE, ACCURATE_DOCUMENT, LOW_LATENCY_

  - [x] 8.5 Build configuration manager component ✅
    - ✅ Create ConfigurationManager class to handle profile loading/saving
    - ✅ Implement runtime profile switching without restart
    - ✅ Add parameter validation with clear error messages
    - ✅ Support custom profile creation and persistence
    - ✅ Store configuration in ~/.personalparakeet/config.toml
    - _Requirements: 15.7, 15.8, 15.9_
    - _Files: personalparakeet/config.py - ConfigurationManager class_

  - [x] 8.6 Integrate configuration with SimpleDictation ✅
    - ✅ Update SimpleDictation to accept ConfigurationManager
    - ✅ Apply configuration parameters to all relevant components
    - ✅ Implement _apply_configuration_changes() for runtime updates
    - ✅ Update TranscriptionProcessor with configurable parameters
    - _Requirements: 15.10_
    - _Files: personalparakeet/dictation.py - SimpleDictation integration_

  - [ ] 8.7 Add configuration UI components (optional)
    - Create profile selector dropdown for quick switching
    - Add parameter sliders with validation ranges
    - Implement trade-off visualization (accuracy vs responsiveness)
    - Show impact of configuration changes in real-time
    - _Requirements: 15.10_

- [ ] 10. Create comprehensive testing suite
  - [ ] 9.1 Add unit tests for LocalAgreement system
    - Test agreement tracking with various transcription patterns
    - Verify timeout handling and edge cases
    - Test performance with long transcription sessions
    - _Requirements: 13.1_
    - _Files: Test ESSENTIAL_LocalAgreement_Code.py_

  - [ ] 9.2 Create integration tests for audio pipeline
    - Test end-to-end audio capture → transcription → output flow
    - Verify error recovery mechanisms
    - Test performance under various load conditions
    - _Requirements: 13.2, 13.3_

  - [ ] 9.3 Add compatibility testing
    - Test across different Windows versions and hardware
    - Verify functionality with various audio devices
    - Test application compatibility for text injection
    - _Requirements: 13.5_

## Future Enhancement Tasks (Post-MVP)

- [ ] 13. Implement LLM integration system
  - [ ] 13.1 Create LLM provider abstraction
    - Implement Ollama integration for local LLM processing
    - Add OpenAI and Google Gemini provider support
    - Create LLM configuration and API key management
    - _Requirements: 8.2, 8.3_

  - [ ] 13.2 Implement F5 LLM refinement feature
    - Create text refinement pipeline with context awareness
    - Add streaming response handling with real-time feedback
    - Implement graceful fallback when LLM processing fails
    - _Requirements: 8.1, 8.4, 8.5_

  - [ ] 13.3 Add context-aware enhancement (F1+F4)
    - Implement application context detection for enhancement
    - Create surrounding text context extraction
    - Add application-specific enhancement prompts
    - _Requirements: 8.6, 5.3_

- [ ] 14. Advanced features and polish
  - [ ] 14.1 Implement multi-language support
    - Add language detection and model switching
    - Create language-specific configuration profiles
    - Implement Unicode text handling for international characters

  - [ ] 14.2 Create advanced UI features
    - Add customizable overlay positioning and transparency
    - Implement keyboard shortcuts for advanced functions
    - Create settings UI for configuration management

  - [ ] 14.3 Add productivity enhancements
    - Implement text templates and macros
    - Create dictation history and replay functionality
    - Add integration with popular productivity applications

## Implementation Notes

### Development Environment Setup
```bash
# Python 3.11 virtual environment
uv venv --python 3.11 .venv
.venv\Scripts\activate

# Core dependencies
pip install nemo-toolkit[asr] sounddevice numpy keyboard

# Testing dependencies  
pip install pytest pytest-asyncio pytest-mock

# Development dependencies
pip install black isort mypy
```

### Testing Strategy
- Unit tests should cover individual component functionality
- Integration tests should use real hardware when possible
- Performance tests should measure against target latencies (150-700ms)
- Error scenario tests should validate all recovery mechanisms

### Code Quality Standards
- Type hints required for all public interfaces
- Docstrings required for all classes and public methods
- Error handling required for all external dependencies
- Logging required for all significant operations

### Performance Targets
- End-to-end latency: 150-700ms (audio capture to text injection)
- Memory usage: <4GB total system footprint
- GPU utilization: 70-90% efficient utilization
- Hotkey response: <50ms for F4 toggle

This implementation plan prioritizes the proven working components first, then builds out the advanced features systematically. Each task is designed to be executable by a coding agent with clear objectives and requirements traceability.