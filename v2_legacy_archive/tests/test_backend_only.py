#!/usr/bin/env python3
"""
Test the backend WebSocket server directly without UI
"""

import asyncio
import websockets
import json
import time

async def test_backend():
    uri = "ws://127.0.0.1:8765"
    
    print("🔌 Connecting to WebSocket backend...")
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to backend!")
            
            # Send initial connection message
            await websocket.send(json.dumps({
                "type": "connection",
                "data": {"client": "test"}
            }))
            
            print("\n📡 Listening for messages from backend...")
            print("Speak into your microphone to test transcription...\n")
            
            # Listen for messages
            start_time = time.time()
            message_count = 0
            
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    print(f"\n[{time.strftime('%H:%M:%S')}] Message #{message_count}:")
                    print(f"Type: {data.get('type', 'unknown')}")
                    
                    if data['type'] == 'transcription':
                        print(f"📝 Transcription: {data.get('data', {}).get('text', '')}")
                        print(f"   Timestamp: {data.get('data', {}).get('timestamp', '')}")
                        
                    elif data['type'] == 'correction':
                        print(f"✨ Clarity Correction:")
                        print(f"   Original: {data.get('data', {}).get('original', '')}")
                        print(f"   Corrected: {data.get('data', {}).get('corrected', '')}")
                        
                    elif data['type'] == 'thought_linking':
                        print(f"🧠 Thought Linking Decision: {data.get('data', {}).get('decision', '')}")
                        
                    elif data['type'] == 'command':
                        print(f"🎤 Command Mode: {data.get('data', {}).get('status', '')}")
                        
                    elif data['type'] == 'status':
                        print(f"ℹ️  Status: {data.get('data', {})}")
                        
                    else:
                        print(f"   Data: {data.get('data', {})}")
                        
                except asyncio.TimeoutError:
                    elapsed = int(time.time() - start_time)
                    print(f"\n⏱️  No messages for 30s (total time: {elapsed}s)")
                    print("Still listening... (speak to test)")
                    
    except (ConnectionRefusedError, OSError):
        print("❌ Cannot connect to backend! Is it running?")
        print("   Start with: python dictation_websocket_bridge.py")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    print("=== PersonalParakeet Backend Test ===\n")
    asyncio.run(test_backend())