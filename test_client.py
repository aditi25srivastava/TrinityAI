import asyncio
import websockets
import json

async def test_chat():
    uri = "ws://localhost:8001/ws/chat"
    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("Connected! Type a message or 'quit' to exit.")
            
            while True:
                message = await asyncio.to_thread(input, "\nYou: ")
                if message.lower() == 'quit':
                    break
                    
                payload = {
                    "text": message,
                    "personality": "Professional"
                }
                
                print("Sending to Trinity AI...")
                await websocket.send(json.dumps(payload))
                
                response = await websocket.recv()
                data = json.loads(response)
                
                print(f"\nTrinity AI: {data.get('text')}")
                
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat())
