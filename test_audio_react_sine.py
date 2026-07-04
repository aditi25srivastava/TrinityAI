import asyncio
import base64
import math
import struct
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

async def test():
    # Generate 2 seconds of 440Hz sine wave at 16000Hz
    sample_rate = 16000
    duration = 2.0
    frequency = 440.0
    num_samples = int(sample_rate * duration)
    
    pcm_bytes = bytearray()
    for i in range(num_samples):
        t = float(i) / sample_rate
        sample = math.sin(2.0 * math.pi * frequency * t)
        pcm_val = int(sample * 32767)
        pcm_bytes.extend(struct.pack('<h', pcm_val))
        
    data_size = len(pcm_bytes)
    wav_header = struct.pack(
        '<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + data_size, b'WAVE',
        b'fmt ', 16, 1, 1, sample_rate,
        sample_rate * 2, 2, 16,
        b'data', data_size
    )
    wav_bytes = wav_header + pcm_bytes
    wav_b64 = base64.b64encode(wav_bytes).decode('utf-8')
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    content = [
        {"type": "text", "text": "This audio contains my spoken message. Please listen to it, follow any commands I give you, and respond naturally. The audio should be a sine wave beep."},
        {"type": "media", "mime_type": "audio/wav", "data": wav_b64}
    ]
    
    agent = create_react_agent(llm, tools=[])
    
    print("Invoking agent...")
    try:
        res = await agent.ainvoke({"messages": [HumanMessage(content=content)]})
        print("RESULT:", res["messages"][-1].content)
    except Exception as e:
        print("ERROR:", e)

asyncio.run(test())
