#!/usr/bin/env python3
"""
WebSocket Bridge for Workshop Box UI
Connects PersonalParakeet dictation to Tauri frontend
"""

import asyncio
import websockets
import json
import logging
import re
from typing import Optional
from dataclasses import dataclass, asdict
import threading
import queue

# Import existing PersonalParakeet components
from personalparakeet.dictation import SimpleDictation
from personalparakeet.clarity_engine import ClarityEngine, CorrectionResult
from personalparakeet.vad_engine import VoiceActivityDetector
from personalparakeet.config_manager import get_config, VADSettings
from personalparakeet.thought_linking import create_thought_linker, LinkingDecision
from personalparakeet.command_mode import create_command_mode_engine, CommandMatch
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


@dataclass
class CommandMessage:
    command: str
    parameters: Optional[dict] = None
    status: str = "executed"  # executed, failed, recognized
    result: Optional[str] = None
    type: str = "command"


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
        
        # Initialize Intelligent Thought Linker
        self.logger.info("Initializing Intelligent Thought Linker...")
        self.thought_linker = create_thought_linker(
            cursor_movement_threshold=100,
            similarity_threshold=0.3,
            timeout_threshold=30.0
        )
        
        # Initialize Command Mode Engine
        self.logger.info("Initializing Command Mode Engine...")
        self.command_engine = create_command_mode_engine(
            activation_phrase="parakeet command",
            activation_confidence_threshold=0.8,
            command_timeout=5.0
        )
        
        # Set up command mode callbacks
        self.command_engine.on_activation_detected = self.handle_command_activation
        self.command_engine.on_command_executed = self.handle_command_execution
        self.command_engine.on_command_timeout = self.handle_command_timeout
        self.command_engine.on_state_changed = self.handle_command_state_change
        
        # Current transcription state
        self.current_text = ""
        self.is_listening = False
        self.clarity_enabled = True
        self.command_mode_enabled = True
        
        # Command mode is now handled by the Command Mode Engine
        # (Old command patterns removed in favor of new system)
        
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
        elif command == "enable_clarity":
            await self.set_clarity_enabled(True)
        elif command == "disable_clarity":
            await self.set_clarity_enabled(False)
        elif command == "toggle_command_mode":
            self.command_mode_enabled = not self.command_mode_enabled
            await self.broadcast({
                "type": "command_mode_status",
                "enabled": self.command_mode_enabled
            })
        elif command == "register_user_action":
            # Register user action for thought linking
            action = data.get("action", "")
            if action:
                self.thought_linker.register_user_action(action)
                self.logger.debug(f"User action registered for thought linking: {action}")
        elif command == "get_status":
            await websocket.send(json.dumps({
                "type": "status",
                "is_listening": self.is_listening,
                "clarity_enabled": self.clarity_enabled,
                "command_mode_enabled": self.command_mode_enabled
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
            # Use Intelligent Thought Linking to determine commit action
            decision, signals = self.thought_linker.should_link_thoughts(self.current_text)
            
            # Log the decision for debugging
            signal_descriptions = [s.description for s in signals]
            self.logger.info(f"Thought linking decision: {decision.value}")
            if signal_descriptions:
                self.logger.info(f"Signals considered: {', '.join(signal_descriptions)}")
            
            # Determine the commit action based on linking decision
            commit_action = "commit_and_continue"  # Default
            
            if decision == LinkingDecision.APPEND_WITH_SPACE:
                commit_action = "append_with_space"
            elif decision == LinkingDecision.START_NEW_PARAGRAPH:
                commit_action = "start_new_paragraph"
            elif decision == LinkingDecision.START_NEW_THOUGHT:
                commit_action = "start_new_thought"
            
            # Send final text to UI for injection with appropriate action
            await self.broadcast({
                "type": "commit_text",
                "text": self.current_text,
                "action": commit_action,
                "linking_decision": decision.value,
                "signals": [{"type": s.signal_type.value, "strength": s.strength, "description": s.description} for s in signals]
            })
            
            # Clear current text
            self.current_text = ""
            self.clarity_engine.clear_context()
    
    async def clear_current_text(self):
        """Clear the current text without committing"""
        self.current_text = ""
        self.clarity_engine.clear_context()
        self.thought_linker.clear_context()  # Clear thought linking context too
        
        await self.broadcast({
            "type": "clear_text"
        })
    
    async def set_clarity_enabled(self, enabled: bool):
        """Set clarity engine enabled state"""
        self.clarity_enabled = enabled
        await self.broadcast({
            "type": "clarity_status",
            "enabled": self.clarity_enabled
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
                # Skip VAD broadcasting from audio thread to avoid threading issues
                # VAD status will be handled in the main process_transcription flow
                self.dictation.audio_callback(indata, frames, time, status)

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
        """Process transcription through Command Mode and Clarity Engine"""
        # Process through Command Mode Engine first if enabled
        if self.command_mode_enabled:
            command_match = self.command_engine.process_speech(text)
            if command_match:
                # Command processed - don't treat as regular transcription
                # Command execution is handled by callbacks
                return
        
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
    
    def on_correction_complete(self, result: CorrectionResult):
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
    
    # Command Mode Engine Callbacks
    
    def handle_command_activation(self):
        """Handle command mode activation"""
        self.logger.info("Command mode activated - waiting for command")
        
        # Send activation feedback to UI with visual indicator
        asyncio.run_coroutine_threadsafe(
            self.broadcast({
                "type": "command_mode_activated",
                "message": "Command mode active - speak your command",
                "visual_feedback": "border_flash_blue"
            }),
            asyncio.get_event_loop()
        )
    
    def handle_command_execution(self, command_match: CommandMatch):
        """Handle command execution"""
        command_id = command_match.command_id
        
        # Send command recognition feedback to UI
        recognition_message = CommandMessage(
            command=command_id,
            status="recognized",
            result=f"Executing: {command_match.description}"
        )
        
        asyncio.run_coroutine_threadsafe(
            self.broadcast(asdict(recognition_message)),
            asyncio.get_event_loop()
        )
        
        # Execute the actual command
        asyncio.run_coroutine_threadsafe(
            self._execute_command_action(command_match),
            asyncio.get_event_loop()
        )
    
    def handle_command_timeout(self):
        """Handle command mode timeout"""
        self.logger.info("Command mode timeout")
        
        asyncio.run_coroutine_threadsafe(
            self.broadcast({
                "type": "command_mode_timeout",
                "message": "Command mode timeout - returning to normal dictation"
            }),
            asyncio.get_event_loop()
        )
    
    def handle_command_state_change(self, new_state):
        """Handle command mode state changes"""
        self.logger.debug(f"Command mode state changed to: {new_state.value}")
        
        asyncio.run_coroutine_threadsafe(
            self.broadcast({
                "type": "command_mode_state",
                "state": new_state.value,
                "is_active": new_state.value != "listening_for_activation"
            }),
            asyncio.get_event_loop()
        )
    
    async def _execute_command_action(self, command_match: CommandMatch):
        """Execute the actual command action"""
        command_id = command_match.command_id
        
        try:
            result = ""
            
            # Execute based on command ID
            if command_id == 'commit_text':
                await self.commit_current_text()
                result = "Text committed"
            elif command_id == 'clear_text':
                await self.clear_current_text()
                result = "Text cleared"
            elif command_id == 'enable_clarity':
                await self.set_clarity_enabled(True)
                result = "Clarity enabled"
            elif command_id == 'disable_clarity':
                await self.set_clarity_enabled(False)
                result = "Clarity disabled"
            elif command_id == 'toggle_clarity':
                await self.set_clarity_enabled(not self.clarity_enabled)
                result = f"Clarity {'enabled' if self.clarity_enabled else 'disabled'}"
            elif command_id == 'start_listening':
                await self.start_dictation()
                result = "Dictation started"
            elif command_id == 'stop_listening':
                await self.stop_dictation()
                result = "Dictation stopped"
            elif command_id == 'show_status':
                status_info = {
                    "listening": self.is_listening,
                    "clarity_enabled": self.clarity_enabled,
                    "command_mode_enabled": self.command_mode_enabled,
                    "current_text_length": len(self.current_text)
                }
                result = f"Status: {status_info}"
                await self.broadcast({
                    "type": "system_status",
                    "status": status_info
                })
            elif command_id == 'exit_command_mode':
                self.command_engine.force_exit_command_mode()
                result = "Exited command mode"
            else:
                result = f"Unknown command: {command_id}"
                
            # Send execution result to UI
            execution_message = CommandMessage(
                command=command_id,
                status="executed",
                result=result
            )
            
            await self.broadcast(asdict(execution_message))
            self.logger.info(f"Command executed: {command_id} - {result}")
            
        except Exception as e:
            # Send error feedback to UI
            error_message = CommandMessage(
                command=command_id,
                status="failed",
                result=f"Error: {str(e)}"
            )
            
            await self.broadcast(asdict(error_message))
            self.logger.error(f"Command execution failed: {command_id} - {e}")
            
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