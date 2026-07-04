import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
import os

load_dotenv()

async def test():
    wav_b64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest")
    agent = create_react_agent(llm, tools=[])
    
    content = [
        {"type": "text", "text": "What is the sound in this audio?"},
        {"type": "media", "mime_type": "audio/wav", "data": wav_b64}
    ]
    state = {"messages": [HumanMessage(content=content)]}
    try:
        res = await agent.ainvoke(state)
        print("RESULT:", res["messages"][-1].content)
    except Exception as e:
        print("ERROR:", e)

asyncio.run(test())
