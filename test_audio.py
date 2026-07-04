import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import base64

load_dotenv()

async def main():
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
    
    # Create a tiny valid wav file in base64 (just a header basically)
    # Actually, we don't even need a real audio file to see if it throws an error or ignores it.
    # Let's just pass a base64 encoded string of "hello" as wav to see if it complains.
    dummy_wav = b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
    wav_b64 = base64.b64encode(dummy_wav).decode('utf-8')
    
    content = [
        {"type": "text", "text": "What is this?"},
        {"type": "image_url", "image_url": {"url": f"data:audio/wav;base64,{wav_b64}"}}
    ]
    
    try:
        response = await llm.ainvoke([HumanMessage(content=content)])
        print("Response:", response.content)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
