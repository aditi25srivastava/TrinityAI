import asyncio
import websockets
import json
import base64
import time

async def main():
    wav_b64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    payload = json.dumps({
        "personality": "Professional",
        "audio_b64": wav_b64
    })
    try:
        start = time.time()
        async with websockets.connect("ws://localhost:8001/ws/chat") as ws:
            print("Connected! Sending payload...")
            await ws.send(payload)
            response = await ws.recv()
            print(f"Received response in {time.time() - start:.2f}s:")
            res_dict = json.loads(response)
            print("AI:", res_dict.get("text"))
    except Exception as e:
        print("ERROR:", e)

asyncio.run(main())
