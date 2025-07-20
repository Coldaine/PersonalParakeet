#!/usr/bin/env python3
"""
WebSocket Bridge for Workshop Box UI
Connects PersonalParakeet dictation to Tauri frontend
"""

import asyncio
import websockets
import json
import logging
from typing import Optional
from dataclasses import dataclass, asdict
import threading
import queue

# Import existing PersonalParakeet components
from personalparakeet.dictation import SimpleDictation
from personalparakeet.clarity_engine import ClarityEngine, CorrectionResult
from personalparakeet.vad_engine import VoiceActivityDetector
from personalparakeet.config_manager import get_config, VADSettings
import sounddevice as sd
import numpy as np


@dataclass
class TranscriptionMessage:
    text: str
    mode: str = "standard"
    confidence: float = 0.0
    type: str = "transcription"
    corrected_text: Optional[str] = None
    correction_time_ms: Optional[float] = None
    corrections_made: Optional[list] = None


class DictationWebSocketBridge:
    """Bridge between PersonalParakeet and Dictation View UI"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.message_queue = queue.Queue()
        self.config = get_config()
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize dictation system
        self.logger.info("Initializing PersonalParakeet dictation system...")
        try:
            # Import cuda fix for RTX 5090
            from personalparakeet.cuda_fix import ensure_cuda_available
            ensure_cuda_available()
            
            # Initialize dictation with proper config
            self.dictation = SimpleDictation(
                device_index=self.config.audio_device_index,  # Use default audio device
                agreement_threshold=1,  # Direct passthrough for v2
                chunk_duration=0.5  # Smaller chunks for responsive UI
            )
            self.logger.info("Dictation system initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize dictation: {e}")
            self.dictation = None
        
        # Initialize Clarity Engine
        self.logger.info("Initializing Clarity Engine...")
        self.clarity_engine = ClarityEngine(enable_rule_based=True)

        # Initialize VAD Engine
        self.vad = VoiceActivityDetector(
            sample_rate=self.config.sample_rate,
            silence_threshold=self.config.vad.custom_threshold or 0.01,
            pause_threshold=self.config.vad.pause_duration_ms / 1000.0
        )
        self.vad.on_pause_detected = self.handle_pause_detected
        
        # Current transcription state
        self.current_text = ""
        self.is_listening = False
        self.clarity_enabled = True
        
    async def register(self, websocket):
        """Register a new client"""
        self.clients.add(websocket)
        self.logger.info(f"Client {websocket.remote_address} connected")
        
    async def unregister(self, websocket):
        """Unregister a client"""
        self.clients.remove(websocket)
        self.logger.info(f"Client {websocket.remote_address} disconnected")
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if self.clients:
            message_json = json.dumps(message)
            await asyncio.gather(
                *[client.send(message_json) for client in self.clients],
                return_exceptions=True
            )
            
    async def handle_client(self, websocket, path):
        """Handle a client connection"""
        await self.register(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.handle_message(data, websocket)
        finally:
            await self.unregister(websocket)
            
    async def handle_message(self, data: dict, websocket):
        """Handle incoming messages from clients"""
        command = data.get("command")
        
        if command == "start_listening":
            await self.start_dictation()
        elif command == "stop_listening":
            await self.stop_dictation()
        elif command == "toggle_clarity":
            self.clarity_enabled = not self.clarity_enabled
            await self.broadcast({
                "type": "clarity_status",
                "enabled": self.clarity_enabled
            })
        elif command == "commit_text":
            await self.commit_current_text()
        elif command == "clear_text":
            await self.clear_current_text()
        elif command == "get_status":
            await websocket.send(json.dumps({
                "type": "status",
                "is_listening": self.is_listening
            }))
            
    async def initialize_clarity_engine(self):
        """Initialize the Clarity Engine asynchronously"""
        try:
            success = await self.clarity_engine.initialize()
            if success:
                self.clarity_engine.start_worker()
                self.logger.info("Clarity Engine initialized and started")
            else:
                self.logger.warning("Clarity Engine initialization failed, continuing without LLM corrections")
        except Exception as e:
            self.logger.error(f"Failed to initialize Clarity Engine: {e}")
    
    async def start_dictation(self):
        """Start the dictation system"""
        if not self.is_listening:
            self.is_listening = True
            self.logger.info("Starting dictation...")
            
            # Initialize Clarity Engine if not already done
            if not self.clarity_engine.is_initialized:
                await self.initialize_clarity_engine()
            
            # Start audio processing in a separate thread
            self.audio_thread = threading.Thread(target=self.audio_loop)
            self.audio_thread.start()
            
            # Broadcast status
            await self.broadcast({
                "type": "dictation_status",
                "is_listening": True,
                "clarity_enabled": self.clarity_enabled
            })
            
    async def stop_dictation(self):
        """Stop the dictation system"""
        if self.is_listening:
            self.is_listening = False
            self.logger.info("Stopping dictation...")
            
            # Broadcast status
            await self.broadcast({
                "type": "dictation_status",
                "is_listening": False
            })
    
    def handle_pause_detected(self, pause_duration: float):
        """Handle automatic commit trigger from VAD"""
        if self.current_text.strip():
            # Trigger commit & continue action
            self.logger.info(f"Pause of {pause_duration:.2f}s detected, committing text.")
            asyncio.run_coroutine_threadsafe(self.commit_current_text(), asyncio.get_event_loop())

    async def commit_current_text(self):
        """Commit the current text and clear the dictation view"""
        if self.current_text.strip():
            # Send final text to UI for injection
            await self.broadcast({
                "type": "commit_text",
                "text": self.current_text,
                "action": "commit_and_continue"
            })
            
            # Clear current text
            self.current_text = ""
            self.clarity_engine.clear_context()
    
    async def clear_current_text(self):
        """Clear the current text without committing"""
        self.current_text = ""
        self.clarity_engine.clear_context()
        
        await self.broadcast({
            "type": "clear_text"
        })
            
    def audio_loop(self):
        """Audio processing loop with Clarity Engine integration"""
        if not self.dictation:
            self.logger.error("Dictation system not initialized")
            return
            
        try:
            # Set up text output callback for real-time transcription
            def on_text_output(text):
                """Callback when dictation produces text"""
                self.process_transcription(text)

            def audio_callback(indata, frames, time, status):
                if status:
                    self.logger.warning(status)
                vad_status = self.vad.process_audio_frame(indata)
                asyncio.run_coroutine_threadsafe(
                    self.broadcast({'type': 'vad_status', 'data': vad_status}),
                    asyncio.get_event_loop()
                )
                self.dictation.process_audio(indata.tobytes())

            # Set the callback if dictation supports it
            if hasattr(self.dictation, 'set_text_output_callback'):
                self.dictation.set_text_output_callback(on_text_output)
            
            # Use the dictation system's own audio handling
            self.dictation.is_recording = True
            
            with sd.InputStream(samplerate=self.config.sample_rate, 
                                 channels=1, 
                                 dtype='float32', 
                                 callback=audio_callback):
                while self.is_listening:
                    import time
                    time.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Audio loop error: {e}")
            self.is_listening = False
        finally:
            if self.dictation:
                if hasattr(self.dictation, 'stop_recording'):
                    self.dictation.stop_recording()
                else:
                    self.dictation.stop_dictation()
    
    def process_transcription(self, text: str):
        """Process transcription through Clarity Engine"""
        # Update current text
        self.current_text = text
        
        # Send raw transcription to UI immediately
        raw_message = TranscriptionMessage(
            text=text,
            confidence=0.8,
            type="raw_transcription"
        )
        
        asyncio.run_coroutine_threadsafe(
            self.broadcast(asdict(raw_message)),
            asyncio.get_event_loop()
        )
        
        # Process through Clarity Engine if enabled
        if self.clarity_enabled and self.clarity_engine.is_initialized:
            # Update context for better corrections
            self.clarity_engine.update_context(text)
            
            # Queue for async correction
            self.clarity_engine.correct_text_async(
                text, 
                callback=self.on_correction_complete
            )
    
    def on_correction_.pycomplete(self, result: CorrectionResult):
        """Callback when Clarity Engine completes correction"""
        # Send corrected text to UI
        corrected_message = TranscriptionMessage(
            text=result.original_text,
            corrected_text=result.corrected_text,
            confidence=result.confidence,
            correction_time_ms=result.processing_time_ms,
            corrections_made=result.corrections_made,
            type="corrected_transcription"
        )
        
        # Update current text with corrected version
        self.current_text = result.corrected_text
        
        # Send to UI
        asyncio.run_coroutine_threadsafe(
            self.broadcast(asdict(corrected_message)),
            asyncio.get_event_loop()
        )
        
        # Log performance
        if result.processing_time_ms > 150:
            self.logger.warning(f"Correction took {result.processing_time_ms:.1f}ms (target: <150ms)")
            
    async def start_server(self):
        """Start the WebSocket server"""
        self.loop = asyncio.get_event_loop()
        
        # Initialize Clarity Engine
        await self.initialize_clarity_engine()
        
        # Start dictation automatically
        await self.start_dictation()
        
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port
        ):
            self.logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            self.logger.info("Dictation and Clarity Engine started automatically")
            await asyncio.Future()  # Run forever
            

def main():
    """Main entry point"""
    bridge = DictationWebSocketBridge()
    asyncio.run(bridge.start_server())
    

if __name__ == "__main__":
    main()