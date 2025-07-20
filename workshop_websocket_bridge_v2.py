#!/usr/bin/env python3
"""
WebSocket Bridge for Workshop Box UI - V2 with proper integration
Connects PersonalParakeet dictation to Tauri frontend
"""

import asyncio
import websockets
import json
import logging
from typing import Optional, Set
from dataclasses import dataclass, asdict
import threading
import time

# Import existing PersonalParakeet components
try:
    from personalparakeet.dictation import SimpleDictation
    from personalparakeet.cuda_fix import ensure_cuda_available
    DICTATION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import dictation components: {e}")
    DICTATION_AVAILABLE = False

# Check CUDA availability
if DICTATION_AVAILABLE:
    cuda_available = ensure_cuda_available()
    if not cuda_available:
        print("Warning: Running without GPU acceleration")


@dataclass
class TranscriptionMessage:
    text: str
    mode: str = "standard"
    confidence: float = 0.95
    type: str = "transcription"


class WorkshopWebSocketBridge:
    """Bridge between PersonalParakeet and Workshop Box UI"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.latest_text = ""
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize dictation system
        self.logger.info("Initializing PersonalParakeet dictation system...")
        self.dictation = None
        self.is_listening = False
        self.loop = None
        
        # Initialize dictation in a separate method to handle errors
        self._init_dictation()
        
    def _init_dictation(self):
        """Initialize the dictation system with proper error handling"""
        if not DICTATION_AVAILABLE:
            self.logger.error("Dictation components not available")
            return
            
        try:
            # Create a custom dictation instance for v2
            self.dictation = SimpleDictation(
                audio_input_callback=None,
                stt_callback=None,
                device_index=None,
                agreement_threshold=1,  # Direct passthrough for v2
                chunk_duration=0.5
            )
            
            # Override the text output callback to send to WebSocket
            original_output = self.dictation.output_text
            
            def websocket_output(text: str):
                """Intercept text output and send to WebSocket clients"""
                # Store latest text
                self.latest_text = text
                
                # Determine mode based on text length
                words = text.split()
                word_count = len(words)
                
                if word_count <= 10:
                    mode = "compact"
                elif word_count <= 50:
                    mode = "standard"
                else:
                    mode = "extended"
                
                # Create message
                message = TranscriptionMessage(
                    text=text,
                    mode=mode,
                    confidence=0.95
                )
                
                # Send to WebSocket clients
                if self.loop:
                    asyncio.run_coroutine_threadsafe(
                        self.broadcast(asdict(message)),
                        self.loop
                    )
                
                # Call original output method (for local display)
                original_output(text)
            
            # Replace the output callback
            self.dictation.output_text = websocket_output
            self.dictation.processor.set_text_output_callback(websocket_output)
            
            self.logger.info("Dictation system initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dictation: {e}")
            self.dictation = None
    
    async def register(self, websocket):
        """Register a new client"""
        self.clients.add(websocket)
        self.logger.info(f"Client {websocket.remote_address} connected")
        
        # Send current text state to new client
        if self.latest_text:
            words = self.latest_text.split()
            mode = "compact" if len(words) <= 10 else "standard" if len(words) <= 50 else "extended"
            
            message = TranscriptionMessage(
                text=self.latest_text,
                mode=mode
            )
            await websocket.send(json.dumps(asdict(message)))
        
    async def unregister(self, websocket):
        """Unregister a client"""
        self.clients.remove(websocket)
        self.logger.info(f"Client {websocket.remote_address} disconnected")
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if self.clients:
            message_json = json.dumps(message)
            # Use gather to send to all clients concurrently
            disconnected = set()
            
            for client in self.clients:
                try:
                    await client.send(message_json)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
                except Exception as e:
                    self.logger.error(f"Error sending to client: {e}")
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.clients -= disconnected
            
    async def handle_client(self, websocket, path):
        """Handle a client connection"""
        await self.register(websocket)
        try:
            async for message in websocket:
                data = json.loads(message)
                await self.handle_message(data, websocket)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            self.logger.error(f"Error handling client: {e}")
        finally:
            await self.unregister(websocket)
            
    async def handle_message(self, data: dict, websocket):
        """Handle incoming messages from clients"""
        msg_type = data.get("type")
        
        if msg_type == "client_connected":
            self.logger.info(f"Client identified as: {data.get('client', 'unknown')}")
            # Send current status
            await websocket.send(json.dumps({
                "type": "status",
                "is_listening": self.is_listening,
                "has_model": self.dictation is not None
            }))
        elif msg_type == "command":
            command = data.get("command")
            if command == "start_listening":
                self.start_dictation()
            elif command == "stop_listening":
                self.stop_dictation()
            elif command == "get_status":
                await websocket.send(json.dumps({
                    "type": "status",
                    "is_listening": self.is_listening,
                    "has_model": self.dictation is not None
                }))
            
    def start_dictation(self):
        """Start the dictation system"""
        if not self.dictation:
            self.logger.error("Cannot start - dictation system not initialized")
            return
            
        if not self.is_listening:
            self.is_listening = True
            self.logger.info("Starting dictation...")
            
            # Start dictation in a separate thread
            self.dictation_thread = threading.Thread(target=self._run_dictation)
            self.dictation_thread.daemon = True
            self.dictation_thread.start()
            
    def stop_dictation(self):
        """Stop the dictation system"""
        if self.is_listening:
            self.is_listening = False
            self.logger.info("Stopping dictation...")
            
            if self.dictation:
                self.dictation.stop_dictation()
            
    def _run_dictation(self):
        """Run dictation in a separate thread"""
        try:
            if self.dictation:
                # This will block until stopped
                self.dictation.start_dictation()
        except Exception as e:
            self.logger.error(f"Dictation error: {e}")
            self.is_listening = False
            
    async def start_server(self):
        """Start the WebSocket server"""
        self.loop = asyncio.get_event_loop()
        
        # Start dictation automatically
        self.start_dictation()
        
        async with websockets.serve(
            self.handle_client,
            self.host,
            self.port,
            # Add ping/pong to detect disconnected clients
            ping_interval=10,
            ping_timeout=5
        ):
            self.logger.info(f"WebSocket server started on ws://{self.host}:{self.port}")
            self.logger.info("Dictation started automatically")
            self.logger.info("Workshop Box ready - speak into your microphone!")
            
            try:
                await asyncio.Future()  # Run forever
            except KeyboardInterrupt:
                self.logger.info("Shutting down...")
                self.stop_dictation()


def main():
    """Main entry point"""
    bridge = WorkshopWebSocketBridge()
    
    try:
        asyncio.run(bridge.start_server())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()