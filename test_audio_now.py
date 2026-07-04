import asyncio
import os
import base64
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

async def main():
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=os.getenv("GEMINI_API_KEY"), max_retries=0)
    
    # Read a real audio file (test.wav)
    try:
        with open("test.wav", "rb") as f:
            audio_bytes = f.read()
        b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        
        msg = HumanMessage(content=[
            {"type": "text", "text": "What is in this audio?"},
            {"type": "image_url", "image_url": {"url": f"data:audio/wav;base64,{b64_audio}"}}
        ])
        
        res = await llm.ainvoke([msg])
        print("Response:", res.content)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
