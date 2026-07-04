import asyncio
import base64
import os
import struct
from langchain_core.messages import HumanMessage
from app.agents.coordinator import coordinator_graph

async def main():
    wav_b64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    content = [
        {"type": "media", "mime_type": "audio/wav", "data": wav_b64}
    ]
    state = {
        "messages": [HumanMessage(content=content)],
        "selected_personality": "Professional",
        "user_id": "test_user",
        "context": ""
    }
    try:
        result = await asyncio.wait_for(coordinator_graph.ainvoke(state), timeout=25.0)
        print("SUCCESS:", result["messages"][-1].content)
    except Exception as e:
        print("ERROR:", type(e), e)

asyncio.run(main())
