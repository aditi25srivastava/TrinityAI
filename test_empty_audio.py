import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

async def test():
    wav_b64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest")
    
    content = [
        {"type": "text", "text": "This audio contains my spoken message. Please listen to it, follow any commands I give you, and respond naturally."},
        {"type": "media", "mime_type": "audio/wav", "data": wav_b64}
    ]
    try:
        res = await llm.ainvoke([HumanMessage(content=content)])
        print("RESULT:", res.content)
    except Exception as e:
        print("ERROR:", e)

asyncio.run(test())
