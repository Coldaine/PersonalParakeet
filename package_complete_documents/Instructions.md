Implement this parakeet project.

 ask serena to activate this project. ensure it's been activated. 
Continue for as long as possible without my help
Before starting code ipmlementation, create a detailed implementation plan and follow it. 

Continue for as long as possible without my help! But, every time Serena gives you a prompt to stay on task, summarize what you just did for the user and sleep for 15 seconds before resuming. 


## Enhanced One-Shot Implementation Plan: Parakeet Dictation with Core Features

### Project Structure
```
parakeet-dictation/
├── audio_handler.py      # Audio capture + VAD
├── transcriber.py        # Parakeet with streaming buffer
├── text_output.py        # Multiple injection methods
├── llm_refiner.py        # Ollama integration
├── dictation.py          # Main app with all features
├── requirements.txt
├── test_components.py    # Basic component tests (not run)
└── README.md
```

### Implementation Files

**requirements.txt**
```
# Core transcription
torch>=2.0.0
transformers>=4.30.0
accelerate>=0.24.0

# Audio
sounddevice>=0.4.6
numpy>=1.24.0
silero-vad>=4.0.0
webrtcvad>=2.0.10
scipy>=1.11.0

# System integration
pynput>=1.7.6
pygetwindow>=0.0.9
pyperclip>=1.8.2
psutil>=5.9.0

# LLM
ollama>=0.1.0
httpx>=0.24.0
aiohttp>=3.9.0

# Utilities
python-dotenv>=1.0.0
colorama>=0.4.6
rich>=13.0.0

# Windows specific
pywin32>=306; sys_platform == 'win32'
```

**audio_handler.py**
```python
import sounddevice as sd
import numpy as np
import torch
import queue
import threading
from silero_vad import load_silero_vad, get_speech_timestamps
import webrtcvad

class AudioHandler:
    def __init__(self, device_index=None):
        # Audio params
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_duration = 0.3  # 300ms chunks
        self.chunk_samples = int(self.sample_rate * self.chunk_duration)
        
        # Queues
        self.raw_queue = queue.Queue()
        self.speech_queue = queue.Queue()
        
        # VAD setup - dual VAD for better accuracy
        self.silero_model, self.silero_utils = load_silero_vad(onnx=True)
        self.webrtc_vad = webrtcvad.Vad(2)  # Aggressiveness 0-3
        
        # State
        self.is_recording = False
        self.device_index = device_index
        self._find_best_device()
        
    def _find_best_device(self):
        """Auto-detect best audio device"""
        if self.device_index is None:
            devices = sd.query_devices()
            for idx, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    # Prefer USB devices or high-quality inputs
                    if 'usb' in device['name'].lower() or 'high' in device['name'].lower():
                        self.device_index = idx
                        break
                        
    def audio_callback(self, indata, frames, time, status):
        """Callback for continuous audio capture"""
        if status:
            print(f"Audio warning: {status}")
            
        if self.is_recording:
            # Convert to 16-bit PCM for WebRTC VAD
            audio_int16 = (indata * 32767).astype(np.int16)
            self.raw_queue.put((indata.copy(), audio_int16))
            
    def process_vad(self):
        """Separate thread for VAD processing"""
        speech_buffer = []
        silence_chunks = 0
        
        while True:
            try:
                audio_float, audio_int16 = self.raw_queue.get(timeout=0.1)
                
                # WebRTC VAD for quick detection
                is_speech_webrtc = self.webrtc_vad.is_speech(
                    audio_int16.tobytes(), 
                    self.sample_rate
                )
                
                # Silero VAD for confirmation (more accurate)
                audio_tensor = torch.from_numpy(audio_float.flatten())
                speech_prob = self.silero_model(audio_tensor, self.sample_rate).item()
                is_speech_silero = speech_prob > 0.5
                
                # Combine both VADs
                is_speech = is_speech_webrtc or is_speech_silero
                
                if is_speech:
                    speech_buffer.append(audio_float)
                    silence_chunks = 0
                else:
                    silence_chunks += 1
                    
                    # If we had speech and now have silence, send buffer
                    if speech_buffer and silence_chunks > 3:  # ~900ms silence
                        combined_audio = np.concatenate(speech_buffer)
                        self.speech_queue.put(combined_audio)
                        speech_buffer = []
                        
            except queue.Empty:
                continue
                
    def start(self):
        """Start audio capture and VAD processing"""
        self.is_recording = True
        
        # Start VAD thread
        vad_thread = threading.Thread(target=self.process_vad, daemon=True)
        vad_thread.start()
        
        # Start audio stream
        self.stream = sd.InputStream(
            device=self.device_index,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32',
            callback=self.audio_callback,
            blocksize=self.chunk_samples,
            latency='low'
        )
        self.stream.start()
        
    def get_speech_chunk(self):
        """Get next speech chunk if available"""
        try:
            return self.speech_queue.get_nowait()
        except queue.Empty:
            return None
```

**transcriber.py**
```python
import torch
from transformers import AutoModelForCTC, AutoProcessor
import numpy as np
from collections import deque
import time

class StreamingParakeet:
    def __init__(self, device="cuda:0"):
        model_name = "nvidia/parakeet-tdt-0.6b-v2"
        
        # Model setup
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.processor = AutoProcessor.from_pretrained(model_name)
        self.model = AutoModelForCTC.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        # Streaming state
        self.audio_buffer = deque(maxlen=48000)  # 3 seconds max
        self.context_buffer = deque(maxlen=16000)  # 1 second context
        
        # Text state tracking
        self.previous_text = ""
        self.stable_text = ""
        self.pending_text = ""
        self.stability_counter = {}
        
        # Performance tracking
        self.last_process_time = 0
        
    def process_audio(self, audio_chunk):
        """Process audio with streaming logic"""
        # Add to buffer
        self.audio_buffer.extend(audio_chunk.flatten())
        
        # Process if we have enough audio (at least 0.5 seconds)
        if len(self.audio_buffer) < 8000:
            return None
            
        # Prepare audio with context
        current_audio = np.array(self.audio_buffer)
        
        if len(self.context_buffer) > 0:
            # Prepend context for better accuracy
            full_audio = np.concatenate([
                np.array(self.context_buffer),
                current_audio
            ])
        else:
            full_audio = current_audio
            
        # Transcribe
        start_time = time.time()
        text = self._transcribe(full_audio)
        self.last_process_time = time.time() - start_time
        
        # Update streaming state
        result = self._update_text_state(text)
        
        # Keep last second as context
        if len(current_audio) > 16000:
            self.context_buffer = deque(current_audio[-16000:], maxlen=16000)
            
        # Clear main buffer after processing
        self.audio_buffer.clear()
        
        return result
        
    def _transcribe(self, audio_array):
        """Run model inference"""
        with torch.no_grad():
            # Prepare inputs
            inputs = self.processor(
                audio_array,
                sampling_rate=16000,
                return_tensors="pt",
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get logits
            logits = self.model(**inputs).logits
            
            # Decode
            predicted_ids = torch.argmax(logits, dim=-1)
            text = self.processor.batch_decode(predicted_ids)[0]
            
        return text
        
    def _update_text_state(self, new_text):
        """Track text stability for streaming"""
        # Split into words for stability tracking
        words = new_text.split()
        
        # Track word stability
        stable_words = []
        pending_words = []
        
        for i, word in enumerate(words):
            word_key = f"{i}:{word}"
            
            if word_key in self.stability_counter:
                self.stability_counter[word_key] += 1
                if self.stability_counter[word_key] >= 3:  # Stable after 3 appearances
                    stable_words.append(word)
                else:
                    pending_words.append(word)
            else:
                self.stability_counter[word_key] = 1
                pending_words.append(word)
                
        # Clean old stability entries
        current_keys = {f"{i}:{word}" for i, word in enumerate(words)}
        self.stability_counter = {
            k: v for k, v in self.stability_counter.items() 
            if k in current_keys
        }
        
        # Update text states
        new_stable = " ".join(stable_words)
        new_pending = " ".join(pending_words)
        
        # Detect newly committed text
        committed_text = ""
        if len(new_stable) > len(self.stable_text):
            committed_text = new_stable[len(self.stable_text):]
            
        self.stable_text = new_stable
        self.pending_text = new_pending
        
        return {
            'committed': committed_text.strip(),
            'pending': new_pending,
            'stable': new_stable,
            'full': new_text,
            'process_time': self.last_process_time
        }
```

**text_output.py**
```python
from pynput import keyboard, mouse
import pyperclip
import platform
import time
import pygetwindow as gw
import win32gui
import win32process
import psutil

class SmartTextOutput:
    def __init__(self):
        self.kb = keyboard.Controller()
        self.mouse_controller = mouse.Controller()
        self.system = platform.system()
        
        # Application detection patterns
        self.code_editors = [
            'visual studio code', 'vscode', 'code.exe',
            'sublime', 'atom', 'pycharm', 'intellij',
            'vim', 'neovim', 'emacs'
        ]
        
        self.browsers = [
            'chrome', 'firefox', 'edge', 'safari', 'brave'
        ]
        
        self.terminals = [
            'terminal', 'powershell', 'cmd', 'iterm', 'konsole'
        ]
        
    def inject_text(self, text, force_method=None):
        """Smart text injection based on context"""
        if not text:
            return
            
        # Determine method
        if force_method:
            method = force_method
        else:
            method = self._determine_best_method()
            
        # Apply method
        if method == 'paste':
            self._paste_method(text)
        elif method == 'type_fast':
            self._type_fast(text)
        elif method == 'type_natural':
            self._type_natural(text)
        elif method == 'terminal':
            self._terminal_paste(text)
        else:
            self._type_fast(text)  # Default
            
    def _determine_best_method(self):
        """Detect active application and choose method"""
        try:
            if self.system == "Windows":
                # Get active window
                hwnd = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                app_name = process.name().lower()
                window_title = win32gui.GetWindowText(hwnd).lower()
                
                # Check patterns
                if any(editor in app_name or editor in window_title 
                       for editor in self.code_editors):
                    return 'paste'
                    
                if any(browser in app_name for browser in self.browsers):
                    return 'type_fast'
                    
                if any(term in app_name for term in self.terminals):
                    return 'terminal'
                    
            return 'type_fast'
            
        except:
            return 'type_fast'
            
    def _paste_method(self, text):
        """Fast paste via clipboard"""
        old_clipboard = pyperclip.paste()
        pyperclip.copy(text)
        
        # Use appropriate key combo
        if self.system == "Darwin":
            with self.kb.pressed(keyboard.Key.cmd):
                self.kb.press('v')
                self.kb.release('v')
        else:
            with self.kb.pressed(keyboard.Key.ctrl):
                self.kb.press('v')
                self.kb.release('v')
                
        time.sleep(0.05)
        
        # Restore clipboard
        try:
            pyperclip.copy(old_clipboard)
        except:
            pass
            
    def _type_fast(self, text):
        """Type quickly with minimal delay"""
        for char in text:
            self.kb.type(char)
            time.sleep(0.001)
            
    def _type_natural(self, text):
        """Type with natural variation"""
        import random
        for char in text:
            self.kb.type(char)
            # Variable delay for natural feel
            delay = random.uniform(0.03, 0.08)
            if char == ' ':
                delay *= 0.5
            elif char in '.!?':
                delay *= 2
            time.sleep(delay)
            
    def _terminal_paste(self, text):
        """Special handling for terminals"""
        # Many terminals use Shift+Insert or right-click
        if self.system == "Windows":
            # Try right-click paste
            self.mouse_controller.click(mouse.Button.right)
            time.sleep(0.1)
        else:
            # Try Shift+Insert
            with self.kb.pressed(keyboard.Key.shift):
                self.kb.press(keyboard.Key.insert)
                self.kb.release(keyboard.Key.insert)
```

**llm_refiner.py**
```python
import asyncio
import httpx
import json
from typing import Optional

class OllamaRefiner:
    def __init__(self, model="llama2:7b", gpu_device="cuda:1"):
        self.model = model
        self.base_url = "http://localhost:11434"
        self.gpu_device = gpu_device  # Use secondary GPU
        
        # Context window for better refinement
        self.context_window = []
        self.max_context = 5
        
    async def refine_text(self, text: str, context_type: str = "general") -> str:
        """Refine text with context awareness"""
        # Build context prompt
        context_str = ""
        if self.context_window:
            context_str = "Previous text: " + " ".join(self.context_window[-3:])
            
        # Type-specific prompts
        prompts = {
            "general": f"""Fix errors and add punctuation to this transcribed text.
Keep the exact meaning. Previous context: {context_str}
Text: {text}
Fixed text:""",
            
            "code": f"""This is dictated code. Fix syntax and formatting.
Add appropriate spacing and punctuation for code.
Text: {text}
Code:""",
            
            "email": f"""Format this as professional email text.
Fix grammar and add appropriate punctuation.
Text: {text}
Formatted:"""
        }
        
        prompt = prompts.get(context_type, prompts["general"])
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_gpu": 1,
                            "main_gpu": 1  # Use second GPU
                        }
                    },
                    timeout=10.0
                )
                
            if response.status_code == 200:
                result = response.json()
                refined = result['response'].strip()
                
                # Update context
                self.context_window.append(refined)
                if len(self.context_window) > self.max_context:
                    self.context_window.pop(0)
                    
                return refined
            else:
                return text
                
        except Exception as e:
            print(f"LLM error: {e}")
            return text
            
    def classify_context(self, app_name: str) -> str:
        """Determine context type from application"""
        app_lower = app_name.lower()
        
        if any(x in app_lower for x in ['code', 'vim', 'visual studio']):
            return 'code'
        elif any(x in app_lower for x in ['outlook', 'gmail', 'mail']):
            return 'email'
        else:
            return 'general'
```

**dictation.py**
```python
import asyncio
import threading
import time
from pynput import keyboard
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live

from audio_handler import AudioHandler
from transcriber import StreamingParakeet
from text_output import SmartTextOutput
from llm_refiner import OllamaRefiner

class AdvancedDictation:
    def __init__(self):
        # Components
        self.audio = AudioHandler()
        self.transcriber = StreamingParakeet(device="cuda:0")
        self.output = SmartTextOutput()
        self.refiner = OllamaRefiner(gpu_device="cuda:1")
        
        # State
        self.is_active = False
        self.use_llm = True
        self.show_overlay = True
        
        # Console for status
        self.console = Console()
        
        # Stats
        self.words_transcribed = 0
        self.session_start = None
        
        # Hotkeys
        self.setup_hotkeys()
        
    def setup_hotkeys(self):
        """Configure hotkey handlers"""
        def on_activate():
            self.is_active = not self.is_active
            if self.is_active:
                self.session_start = time.time()
                self.console.print("[green]Dictation ACTIVE[/green]")
            else:
                self.console.print("[red]Dictation STOPPED[/red]")
                
        def on_llm_toggle():
            self.use_llm = not self.use_llm
            status = "ON" if self.use_llm else "OFF"
            self.console.print(f"[yellow]LLM Refinement: {status}[/yellow]")
            
        def on_overlay_toggle():
            self.show_overlay = not self.show_overlay
            
        # Global hotkeys
        self.hotkeys = keyboard.GlobalHotKeys({
            '<f4>': on_activate,
            '<f5>': on_llm_toggle,
            '<f6>': on_overlay_toggle,
            '<ctrl>+<alt>+q': lambda: exit(0)
        })
        self.hotkeys.start()
        
    async def process_loop(self):
        """Main processing loop"""
        while True:
            if self.is_active:
                # Get speech chunk from VAD
                speech_chunk = self.audio.get_speech_chunk()
                
                if speech_chunk is not None:
                    # Process through transcriber
                    result = self.transcriber.process_audio(speech_chunk)
                    
                    if result and result['committed']:
                        # Get committed text
                        text = result['committed']
                        
                        # Refine if enabled
                        if self.use_llm:
                            # Detect context
                            context_type = self.refiner.classify_context(
                                self.output._determine_best_method()
                            )
                            
                            # Refine asynchronously
                            text = await self.refiner.refine_text(
                                text, 
                                context_type
                            )
                            
                        # Output text
                        self.output.inject_text(text + " ")
                        
                        # Update stats
                        self.words_transcribed += len(text.split())
                        
                    # Show overlay status
                    if self.show_overlay and result:
                        self.update_overlay(result)
                        
            await asyncio.sleep(0.01)
            
    def update_overlay(self, result):
        """Update status overlay"""
        if self.session_start:
            duration = time.time() - self.session_start
            wpm = (self.words_transcribed / duration) * 60 if duration > 0 else 0
        else:
            wpm = 0
            
        status = f"""
[bold]Dictation Status[/bold]
State: [green]ACTIVE[/green] | LLM: {self.use_llm}
Words: {self.words_transcribed} | WPM: {wpm:.0f}
Pending: {result.get('pending', '')[:50]}...
Process Time: {result.get('process_time', 0)*1000:.0f}ms
GPU Memory: {self.get_gpu_memory()}
"""
        self.console.print(Panel(status, title="Parakeet Dictation"))
        
    def get_gpu_memory(self):
        """Get GPU memory usage"""
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            return f"{info.used // 1024**2}MB / {info.total // 1024**2}MB"
        except:
            return "N/A"
            
    def run(self):
        """Start the system"""
        self.console.print("[bold]Advanced Parakeet Dictation System[/bold]")
        self.console.print("F4: Toggle | F5: LLM | F6: Overlay | Ctrl+Alt+Q: Quit")
        
        # Start audio
        self.audio.start()
        
        # Run async loop
        try:
            asyncio.run(self.process_loop())
        except KeyboardInterrupt:
            self.console.print("\n[red]Shutting down...[/red]")

if __name__ == "__main__":
    dictation = AdvancedDictation()
    dictation.run()
```

**test_components.py**
```python
"""Component tests - DO NOT RUN until after implementation"""
import pytest
import numpy as np
import torch

class TestComponents:
    def test_audio_handler_init(self):
        """Test audio handler initialization"""
        from audio_handler import AudioHandler
        handler = AudioHandler()
        assert handler.sample_rate == 16000
        
    def test_transcriber_device_selection(self):
        """Test GPU device selection"""
        from transcriber import StreamingParakeet
        transcriber = StreamingParakeet()
        assert transcriber.device.type in ['cuda', 'cpu']
        
    def test_text_output_methods(self):
        """Test text output method detection"""
        from text_output import SmartTextOutput
        output = SmartTextOutput()
        method = output._determine_best_method()
        assert method in ['paste', 'type_fast', 'type_natural', 'terminal']
        
    def test_llm_context_classification(self):
        """Test context classification"""
        from llm_refiner import OllamaRefiner
        refiner = OllamaRefiner()
        assert refiner.classify_context('code.exe') == 'code'
        assert refiner.classify_context('outlook') == 'email'
        
    def test_audio_vad_processing(self):
        """Test VAD with mock audio"""
        # Generate mock audio
        mock_audio = np.random.randn(16000).astype(np.float32)
        # Would test VAD processing here
        
    def test_streaming_buffer_logic(self):
        """Test streaming transcription buffer"""
        # Would test buffer accumulation and context
        pass

# DO NOT RUN THESE TESTS
```

**README.md**
```markdown
# Advanced Parakeet Dictation Prototype

Feature-complete dictation system with GPU acceleration, dual VAD, LLM refinement, and smart text injection.

## Features Implemented
- Dual VAD (Silero + WebRTC) for accurate speech detection
- Streaming transcription with context and stability tracking
- Smart text injection based on active application
- LLM refinement with context awareness
- GPU distribution (Parakeet on GPU 0, Ollama on GPU 1)
- Real-time statistics overlay
- Multiple hotkeys for feature control

## Quick Start
```bash
pip install -r requirements.txt
python dictation.py
```

## Hotkeys
- F4: Toggle dictation ON/OFF
- F5: Toggle LLM refinement
- F6: Toggle overlay display
- Ctrl+Alt+Q: Quit

## Architecture
- Audio: 16kHz capture with dual VAD processing
- Transcription: Streaming with 3-second buffer and context
- Output: Smart injection (paste for editors, type for browsers)
- LLM: Context-aware refinement on secondary GPU
```


Add a simple WebSocket server mode (`--server` flag) that streams transcriptions to `ws://localhost:8765`. This would allow other applications to consume the transcription stream without needing text injection, making it useful for custom integrations or debugging. Implementation would be just 20 lines using the `websockets` library.