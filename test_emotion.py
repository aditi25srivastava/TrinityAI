import asyncio
import websockets
import json
import base64

async def test():
    uri = "ws://localhost:8001/ws/chat"
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket.")
        
        # Send an angry prompt
        msg = {
            "text": "You are the worst AI ever created! I hate you!",
            "personality": "Professional"
        }
        await websocket.send(json.dumps(msg))
        print("Sent angry test message...")
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        
        print("\n--- AI RESPONSE ---")
        print(f"Text: {data.get('text')}")
        print(f"Emotion: {data.get('emotion')}")
        print("-------------------\n")

asyncio.run(test())
