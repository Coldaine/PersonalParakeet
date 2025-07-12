# Essential Audio Integration Code
# Basic WebSocket + Audio capture for PersonalParakeet

import asyncio
import numpy as np
import sounddevice as sd
from fastapi import FastAPI, WebSocket
from typing import Optional, Callable
import json

# Basic audio capture class (builds on test_audio_minimal.py)
class AudioCapture:
    """Simple audio capture for real-time dictation"""
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 channels: int = 1,
                 chunk_duration_ms: int = 100):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        self.is_recording = False
        self.audio_callback: Optional[Callable] = None
    
    def set_audio_callback(self, callback: Callable[[np.ndarray], None]):
        """Set callback function to receive audio chunks"""
        self.audio_callback = callback
    
    def start_recording(self):
        """Start audio capture"""
        self.is_recording = True
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            
            if self.audio_callback and self.is_recording:
                # Convert to float32 and flatten
                audio_data = indata[:, 0].astype(np.float32)
                self.audio_callback(audio_data)
        
        # Start the audio stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=audio_callback,
            blocksize=self.chunk_size
        )
        self.stream.start()
        print(f"✅ Audio recording started at {self.sample_rate}Hz")
    
    def stop_recording(self):
        """Stop audio capture"""
        self.is_recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        print("⏹️ Audio recording stopped")

# Simple Voice Activity Detection
class SimpleVAD:
    """Basic energy-based Voice Activity Detection"""
    
    def __init__(self, 
                 energy_threshold: float = 0.01,
                 min_speech_duration_ms: int = 300):
        self.energy_threshold = energy_threshold
        self.min_speech_samples = int(16000 * min_speech_duration_ms / 1000)
        self.speech_buffer = []
        self.is_speech_active = False
    
    def process_audio(self, audio_chunk: np.ndarray) -> Optional[np.ndarray]:
        """
        Process audio chunk and return speech if detected
        
        Returns:
            Complete speech utterance or None if still collecting
        """
        # Calculate energy (RMS)
        energy = np.sqrt(np.mean(audio_chunk ** 2))
        
        if energy > self.energy_threshold:
            # Speech detected
            self.speech_buffer.extend(audio_chunk)
            self.is_speech_active = True
        else:
            # Silence detected
            if self.is_speech_active and len(self.speech_buffer) > self.min_speech_samples:
                # End of speech utterance
                speech_data = np.array(self.speech_buffer, dtype=np.float32)
                self.speech_buffer = []
                self.is_speech_active = False
                return speech_data
            elif not self.is_speech_active:
                # Clear buffer if no speech
                self.speech_buffer = []
        
        # Prevent buffer from growing too large
        if len(self.speech_buffer) > 16000 * 10:  # 10 seconds max
            speech_data = np.array(self.speech_buffer, dtype=np.float32)
            self.speech_buffer = []
            self.is_speech_active = False
            return speech_data
        
        return None

# Basic FastAPI WebSocket integration
class WebSocketTranscriptionServer:
    """Simple WebSocket server for real-time transcription"""
    
    def __init__(self, transcription_callback: Callable[[np.ndarray], str]):
        self.app = FastAPI()
        self.transcription_callback = transcription_callback
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "PersonalParakeet"}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            vad = SimpleVAD()
            
            try:
                while True:
                    # Receive audio data from client
                    data = await websocket.receive_bytes()
                    
                    # Convert bytes to numpy array
                    audio_chunk = np.frombuffer(data, dtype=np.float32)
                    
                    # Process through VAD
                    speech_data = vad.process_audio(audio_chunk)
                    
                    if speech_data is not None:
                        # Send to transcription
                        transcription = self.transcription_callback(speech_data)
                        
                        # Send result back to client
                        await websocket.send_json({
                            "text": transcription,
                            "type": "transcription"
                        })
                    else:
                        # Send status update
                        await websocket.send_json({
                            "status": "processing",
                            "type": "status"
                        })
                        
            except Exception as e:
                print(f"WebSocket error: {e}")
            finally:
                await websocket.close()

# Audio format conversion utilities
def convert_audio_to_16khz_mono(audio_data: np.ndarray, 
                               source_sample_rate: int = 44100) -> np.ndarray:
    """Convert audio to 16kHz mono for transcription"""
    if source_sample_rate == 16000:
        return audio_data
    
    # Simple downsampling (for production, use proper resampling)
    downsample_factor = source_sample_rate // 16000
    if downsample_factor > 1:
        audio_data = audio_data[::downsample_factor]
    
    return audio_data

def audio_to_bytes(audio_data: np.ndarray) -> bytes:
    """Convert numpy audio array to bytes for WebSocket transmission"""
    return audio_data.astype(np.float32).tobytes()

def bytes_to_audio(audio_bytes: bytes) -> np.ndarray:
    """Convert bytes back to numpy audio array"""
    return np.frombuffer(audio_bytes, dtype=np.float32)

# Complete integration example
class RealTimeDictationSystem:
    """Complete real-time dictation system"""
    
    def __init__(self, transcription_model):
        self.transcription_model = transcription_model
        self.audio_capture = AudioCapture()
        self.vad = SimpleVAD()
        self.text_output_callback: Optional[Callable] = None
        
        # Setup audio processing pipeline
        self.audio_capture.set_audio_callback(self.process_audio_chunk)
    
    def process_audio_chunk(self, audio_chunk: np.ndarray):
        """Process incoming audio chunk"""
        speech_data = self.vad.process_audio(audio_chunk)
        
        if speech_data is not None:
            # Transcribe speech
            transcription = self.transcription_model(speech_data)
            
            # Output text
            if self.text_output_callback:
                self.text_output_callback(transcription)
    
    def set_text_output_callback(self, callback: Callable[[str], None]):
        """Set callback for text output"""
        self.text_output_callback = callback
    
    def start_dictation(self):
        """Start real-time dictation"""
        self.audio_capture.start_recording()
        print("🎤 Dictation started")
    
    def stop_dictation(self):
        """Stop real-time dictation"""
        self.audio_capture.stop_recording()
        print("⏹️ Dictation stopped")

# Basic text output (for integration with LocalAgreement)
def output_text_to_system(text: str):
    """Output text to the system (placeholder for actual implementation)"""
    print(f"OUTPUT: {text}")
    # In real implementation, this would use:
    # - keyboard.write(text) for typing
    # - pyperclip.copy(text) + paste for clipboard
    # - platform-specific APIs for smart injection

# WebSocket client example (for testing)
async def websocket_client_example():
    """Example WebSocket client for testing"""
    import websockets
    
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        # Simulate sending audio data
        test_audio = np.random.random(1600).astype(np.float32)  # 100ms of audio
        
        await websocket.send(audio_to_bytes(test_audio))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Received: {data}")

# Example usage
if __name__ == "__main__":
    # Mock transcription function
    def mock_transcription(audio_data: np.ndarray) -> str:
        # In real implementation, this would use Parakeet
        return f"Transcribed {len(audio_data)} audio samples"
    
    # Create WebSocket server
    server = WebSocketTranscriptionServer(mock_transcription)
    
    # Create real-time dictation system
    dictation = RealTimeDictationSystem(mock_transcription)
    dictation.set_text_output_callback(output_text_to_system)
    
    print("Audio integration components ready")
    print("To run WebSocket server: uvicorn this_file:server.app --host 0.0.0.0 --port 8000")
