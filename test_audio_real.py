import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import base64
import wave
import struct
import math

load_dotenv()

async def main():
    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
    
    # Generate 1 sec sine wave (440Hz)
    sample_rate = 16000
    frames = []
    for i in range(sample_rate):
        value = int(32767.0 * math.sin(2.0 * math.pi * 440.0 * i / sample_rate))
        frames.append(struct.pack('<h', value))
    
    with open("test.wav", "wb") as f:
        wav = wave.open(f, "w")
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b''.join(frames))
        wav.close()
        
    with open("test.wav", "rb") as f:
        wav_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    # test both "image_url" and "media" types
    content = [
        {"type": "text", "text": "Describe the sound in the audio."},
        {"type": "image_url", "image_url": {"url": f"data:audio/wav;base64,{wav_b64}"}}
    ]
    
    try:
        response = await llm.ainvoke([HumanMessage(content=content)])
        print("Response using image_url:", response.content)
    except Exception as e:
        print("Error using image_url:", e)

    content2 = [
        {"type": "text", "text": "Describe the sound in the audio."},
        {"type": "media", "mime_type": "audio/wav", "data": wav_b64}
    ]
    
    try:
        response2 = await llm.ainvoke([HumanMessage(content=content2)])
        print("Response using media:", response2.content)
    except Exception as e:
        print("Error using media:", e)

if __name__ == "__main__":
    asyncio.run(main())
