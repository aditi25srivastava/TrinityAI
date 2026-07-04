import asyncio
import websockets
import json

async def main():
    wav_b64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    payload = json.dumps({"personality": "Professional", "audio_b64": wav_b64})
    
    async with websockets.connect("ws://localhost:8001/ws/chat") as ws:
        await ws.send(payload)
        try:
            while True:
                msg = await ws.recv()
                print("RECV:", msg)
        except Exception as e:
            print("WS CLOSED:", type(e), e)

asyncio.run(main())
