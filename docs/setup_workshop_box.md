# Workshop Box Setup Guide

## Prerequisites

1. **Node.js** (v16 or later)
   - Download from: https://nodejs.org/

2. **Rust** (for Tauri)
   - Download from: https://www.rust-lang.org/tools/install
   - Run: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`

3. **Microsoft C++ Build Tools** (Windows only)
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Install "Desktop development with C++" workload

## Installation Steps

### 1. Install Tauri Dependencies

```bash
cd workshop-box-ui

# Install Node dependencies
npm install

# Install Rust dependencies (automatic with first build)
```

### 2. Build the Tauri App

```bash
# Development mode (hot reload)
npm run tauri dev

# Production build
npm run tauri build
```

### 3. Start the Python WebSocket Bridge

In a separate terminal:

```bash
# From PersonalParakeet root directory
.venv\Scripts\python.exe workshop_websocket_bridge.py
```

## Architecture Overview

```
┌─────────────────────────┐
│   Tauri Frontend        │
│  (React + TypeScript)   │
│                         │
│  - Glass morphism UI    │
│  - Smooth animations    │
│  - 3-state sizing       │
└───────────┬─────────────┘
            │ WebSocket
            │ ws://localhost:8765
┌───────────▼─────────────┐
│   Python Backend        │
│  (PersonalParakeet)     │
│                         │
│  - Parakeet STT         │
│  - Audio processing     │
│  - Clarity Engine       │
└─────────────────────────┘
```

## Features Implemented

### UI Components
- ✅ Transparent window with blur effects
- ✅ Glass morphism design
- ✅ Smooth animations (Framer Motion)
- ✅ 3-state adaptive sizing (compact/standard/extended)
- ✅ Status indicators and confidence bars
- ✅ Particle effects for "thinking" state
- ✅ Dark mode support
- ✅ High contrast mode
- ✅ Reduced motion support

### Backend Integration
- ✅ WebSocket communication
- ✅ Real-time transcription streaming
- ✅ Zustand state management
- ✅ Tauri window manipulation APIs

## Development Workflow

### Frontend Development

The UI uses modern web technologies:
- **React** for components
- **TypeScript** for type safety
- **Framer Motion** for animations
- **CSS Modules** for styling

To modify the UI:
1. Edit files in `src/components/`
2. Changes hot-reload automatically
3. Use browser DevTools (F12) for debugging

### Adding New Visual Effects

Example: Add a glow effect when speaking

```tsx
// In WorkshopBox.tsx
<motion.div
  className="glow-effect"
  animate={{
    boxShadow: isListening 
      ? ["0 0 20px rgba(96, 165, 250, 0)", "0 0 40px rgba(96, 165, 250, 0.8)"]
      : "0 0 20px rgba(96, 165, 250, 0)"
  }}
  transition={{ duration: 1, repeat: Infinity, repeatType: "reverse" }}
/>
```

### Python Integration

To send data from Python to UI:

```python
# In workshop_websocket_bridge.py
await self.broadcast({
    "type": "transcription",
    "text": "Hello world",
    "mode": "compact",
    "confidence": 0.95
})
```

## Customization

### Themes

Edit `src/components/WorkshopBox.css`:

```css
/* Custom theme */
.workshop-box.custom-theme {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  backdrop-filter: blur(30px);
}
```

### Animations

All animations use Framer Motion. Example:

```tsx
<motion.div
  whileHover={{ scale: 1.05 }}
  whileTap={{ scale: 0.95 }}
  transition={{ type: "spring", stiffness: 400 }}
>
  Interactive Element
</motion.div>
```

## Troubleshooting

### Common Issues

1. **"Error: could not find `cargo`"**
   - Install Rust: https://rustup.rs/

2. **WebSocket connection failed**
   - Ensure Python bridge is running
   - Check firewall settings

3. **Window not transparent**
   - Windows 11: Enable transparency effects in Settings
   - Linux: Requires compositor (KWin, Compiz, etc.)

### Debug Mode

Enable debug logging:

```rust
// In src-tauri/src/main.rs
env_logger::init();
```

## Next Steps

1. **Clarity Engine Integration**
   - Add LLM for real-time corrections
   - Display corrections with strikethrough

2. **Command Mode**
   - Voice command detection
   - Visual feedback for command state

3. **Intelligent Thought-Linking**
   - Context tracking
   - Semantic similarity analysis

The Workshop Box is now a modern, web-based UI that can be extended with any web technology or library!