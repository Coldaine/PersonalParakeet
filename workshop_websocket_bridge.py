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
from personalparakeet.audio_devices import get_default_input_device
import sounddevice as sd
import numpy as np


@dataclass
class TranscriptionMessage:
    text: str
    mode: str = "standard"
    confidence: float = 0.0
    type: str = "transcription"


class WorkshopWebSocketBridge:
    """Bridge between PersonalParakeet and Workshop Box UI"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.message_queue = queue.Queue()
        
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
                device_index=None,  # Use default audio device
                agreement_threshold=1,  # Direct passthrough for v2
                chunk_duration=0.5  # Smaller chunks for responsive UI
            )
            self.logger.info("Dictation system initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize dictation: {e}")
            self.dictation = None
        
        self.is_listening = False
        
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
            self.start_dictation()
        elif command == "stop_listening":
            self.stop_dictation()
        elif command == "get_status":
            await websocket.send(json.dumps({
                "type": "status",
                "is_listening": self.is_listening
            }))
            
    def start_dictation(self):
        """Start the dictation system"""
        if not self.is_listening:
            self.is_listening = True
            self.logger.info("Starting dictation...")
            
            # Start audio processing in a separate thread
            self.audio_thread = threading.Thread(target=self.audio_loop)
            self.audio_thread.start()
            
    def stop_dictation(self):
        """Stop the dictation system"""
        if self.is_listening:
            self.is_listening = False
            self.logger.info("Stopping dictation...")
            
    def audio_loop(self):
        """Audio processing loop"""
        if not self.dictation:
            self.logger.error("Dictation system not initialized")
            return
            
        try:
            # Use the dictation system's own audio handling
            self.dictation.is_recording = True
            
            # Start the dictation's audio processing
            self.dictation.start_recording()
            
            # Monitor for transcriptions
            while self.is_listening:
                # Check if dictation has produced any text
                # For v2, we want direct passthrough without LocalAgreement buffering
                # So we'll need to hook into the transcription output
                time.sleep(0.1)
                
        except Exception as e:
            self.logger.error(f"Audio loop error: {e}")
            self.is_listening = False
        finally:
            if self.dictation:
                self.dictation.stop_recording()
            
    async def start_server(self):
        """Start the WebSocket server"""
        self.loop = asyncio.get_event_loop()
        
        # Start dictation automatically
        self.start_dictation()
        
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port
        ):
            self.logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            self.logger.info("Dictation started automatically")
            await asyncio.Future()  # Run forever
            

def main():
    """Main entry point"""
    bridge = WorkshopWebSocketBridge()
    asyncio.run(bridge.start_server())
    

if __name__ == "__main__":
    main()