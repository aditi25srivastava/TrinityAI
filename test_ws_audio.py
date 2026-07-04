import asyncio
import websockets
import json
import base64
import math
import struct

async def test_websocket():
    uri = "ws://localhost:8001/ws/chat"
    
    # Generate 1 second of 440Hz sine wave at 48000Hz (simulating Unity)
    sample_rate = 48000
    duration = 1.0
    frequency = 440.0
    num_samples = int(sample_rate * duration)
    
    pcm_bytes = bytearray()
    for i in range(num_samples):
        t = float(i) / sample_rate
        sample = math.sin(2.0 * math.pi * frequency * t)
        pcm_val = int(sample * 32767)
        pcm_bytes.extend(struct.pack('<h', pcm_val))
        
    audio_b64 = base64.b64encode(pcm_bytes).decode('utf-8')
    
    payload = {
        "audio_b64": audio_b64,
        "sample_rate": sample_rate,
        "personality": "Professional"
    }
    
    async with websockets.connect(uri) as websocket:
        print("Connected!")
        await websocket.send(json.dumps(payload))
        print("Sent audio payload")
        
        while True:
            try:
                response = await websocket.recv()
                data = json.loads(response)
                print(f"AI: {data.get('text')} | Emotion: {data.get('emotion')}")
                if data.get('audio_b64'):
                    print("Received audio TTS!")
                break
            except Exception as e:
                print(f"Error receiving: {e}")
                break

asyncio.run(test_websocket())
