import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

async def test():
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=os.getenv("GEMINI_API_KEY"))
    # 1 second of silence in WAV base64
    wav_b64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    msg = HumanMessage(content=[
        {"type": "text", "text": "What is in this audio?"},
        {"type": "image_url", "image_url": {"url": f"data:audio/wav;base64,{wav_b64}"}}
    ])
    try:
        res = await llm.ainvoke([msg])
        print("SUCCESS:", res.content)
    except Exception as e:
        print("ERROR:", e)

asyncio.run(test())
