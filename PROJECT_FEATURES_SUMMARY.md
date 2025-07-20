# PersonalParakeet - Real-Time AI Dictation System v0.1 July 16 2025 11PM

## Project Overview
PersonalParakeet is a sophisticated real-time dictation system that uses NVIDIA's Parakeet-TDT 1.1B model for speech-to-text conversion. The system features a revolutionary "LocalAgreement buffering" approach that prevents jarring text rewrites and provides a superior dictation experience compared to traditional systems.

## Core Technology Stack
- **AI Model**: NVIDIA Parakeet-TDT 1.1B (via NeMo toolkit)
- **GPU Acceleration**: CUDA-optimized for RTX 3090/5090 hardware
- **Cross-Platform**: Windows and Linux support with native optimizations
- **Real-Time Processing**: Sub-second latency with chunked audio processing
- **Direct Integration**: No API wrappers - direct NeMo model integration

## Key Features

### 1. LocalAgreement Buffering System (Core Innovation)
- **Problem Solved**: Traditional dictation systems constantly rewrite text as they receive new audio, creating a jarring user experience
- **Solution**: LocalAgreement buffering tracks word stability across multiple transcription iterations
- **Implementation**: Words must appear consistently across N consecutive transcriptions before being "committed" to output
- **Benefits**: 
  - Smooth, stable text output without jarring rewrites
  - Configurable agreement thresholds (1-5 iterations)
  - Pending text preview shows uncommitted words
  - Timeout system prevents words from staying pending indefinitely

### 2. Intelligent Text Injection System
- **Cross-Platform Support**: 
  - Windows: UI Automation, keyboard simulation, clipboard strategies
  - Linux: XTest, Xdotool, AT-SPI, KDE optimizations
- **Application-Aware**: Different injection strategies for editors, browsers, terminals, IDEs
- **Fallback Chain**: Multiple strategies attempt injection until one succeeds
- **Performance Optimization**: Strategy selection based on application type and platform

### 3. Advanced Audio Processing
- **Real-Time Capture**: 16kHz mono audio with configurable chunk sizes (0.3-2.0 seconds)
- **Device Management**: Smart audio device selection with interactive fallback
- **Noise Handling**: Audio level thresholds to skip silent periods
- **Error Recovery**: GPU memory management and audio stream error handling

### 4. Configuration Management System
- **Multiple Profiles**: Pre-configured settings for different use cases:
  - `fast_conversation`: Low latency for casual conversation
  - `balanced`: Balanced speed/accuracy for general use
  - `accurate_document`: High accuracy for document creation
  - `low_latency`: Minimal processing delay
- **Runtime Switching**: Change profiles without restarting the application
- **Persistent Settings**: Configuration saved to JSON files

### 5. Hotkey Integration
- **F4 Toggle**: Start/stop dictation with configurable hotkey
- **Global Hotkeys**: Works regardless of active application
- **Visual Feedback**: Console logging shows dictation state and text processing

### 6. Application Detection & Targeting
- **Smart Detection**: Automatically identifies active applications
- **Application Types**: Categorizes apps (Editor, Browser, Terminal, IDE, Office, Chat)
- **Optimized Strategies**: Different text injection approaches per app type
- **Window Focus Management**: Ensures text goes to the intended target

## Technical Architecture

### Core Components
1. **`run_dictation.py`**: Main entry point and CLI interface
2. **`personalparakeet/dictation.py`**: Core dictation engine with LocalAgreement integration
3. **`personalparakeet/local_agreement.py`**: LocalAgreement buffering implementation
4. **`personalparakeet/text_injection.py`**: Cross-platform text injection manager
5. **`personalparakeet/config.py`**: Configuration management system
6. **`personalparakeet/audio_devices.py`**: Audio device detection and management

### Cross-Platform Text Injection Strategies
- **Windows**: UI Automation, Keyboard simulation, Clipboard paste
- **Linux X11**: XTest extension, Xdotool, Clipboard
- **Linux Wayland**: AT-SPI, Clipboard fallback
- **KDE Optimization**: Specialized KDE simple injector for Plasma desktop

### GPU and Memory Management
- **CUDA Optimization**: RTX 5090 compatibility fixes
- **Memory Management**: Automatic GPU memory cleanup on errors
- **Model Loading**: Efficient FP16 model loading for reduced memory usage

## User Experience Features

### Real-Time Operation
- **Continuous Dictation**: Speak naturally without pausing for processing
- **Live Feedback**: See pending words while speaking, committed words appear smoothly
- **Natural Flow**: No artificial pauses or waiting for processing

### Error Handling & Recovery
- **Graceful Degradation**: System continues working even if preferred injection method fails
- **Audio Recovery**: Automatic recovery from audio device disconnections
- **GPU Error Handling**: Automatic CUDA memory cleanup and retry logic

### Monitoring & Debugging
- **Comprehensive Logging**: Detailed logs for troubleshooting
- **Performance Metrics**: Processing time and confidence scoring
- **Device Information**: Audio device validation and selection assistance

## Potential GUI Enhancement Areas

### Real-Time Status Display
- **Visual Dictation State**: Clear indication when dictation is active/inactive
- **Text Preview Window**: Show committed vs pending text in real-time
- **Audio Level Meter**: Visual feedback of microphone input levels
- **Confidence Indicator**: Real-time display of transcription confidence

### Configuration Interface
- **Profile Management**: GUI for creating/editing configuration profiles
- **Device Selection**: Visual audio device selection with testing capabilities
- **Hotkey Configuration**: Customizable hotkey assignment interface
- **Strategy Preferences**: Visual selection of text injection strategies

### Application Integration Dashboard
- **Active App Display**: Show currently targeted application
- **Injection Status**: Real-time feedback on text injection success/failure
- **Application Rules**: Configure per-application behavior settings
- **Strategy Performance**: Show which injection methods work best per app

### Advanced Features for GUI
- **Session Management**: Save/load dictation sessions
- **Text History**: Browse and search previously dictated text
- **Performance Analytics**: Charts showing accuracy and speed over time
- **Voice Commands**: GUI controls accessible via voice commands
- **Multi-Language Support**: GUI for switching between language models

## System Requirements
- **Hardware**: NVIDIA GPU (RTX 3090/5090 recommended)
- **Software**: CUDA 12.1+ drivers, Python 3.8+
- **Operating System**: Windows 10/11 or Linux (Ubuntu 20.04+)
- **Audio**: Any standard microphone input device

## Current Status
The system is **fully functional** with proven real-time dictation capabilities. The LocalAgreement buffering system is working effectively to provide smooth text output, and cross-platform text injection is operational on both Windows and Linux environments.