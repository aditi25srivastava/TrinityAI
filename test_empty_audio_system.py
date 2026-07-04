import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

async def test():
    wav_b64 = "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    llm = ChatGoogleGenerativeAI(model="gemini-flash-latest")
    
    sys_prompt = "You are a research assistant and an autonomous AI Agent. You have access to tools that can affect the real world.\n\nCRITICAL INSTRUCTION: If the user asks you to perform an action (like opening an application, scheduling a meeting, or generating a report), YOU MUST CALL THE CORRESPONDING TOOL IMMEDIATELY. Do not just talk about it.\n\nPersonality: Professional. Context: . Past Memories about this user: .\n**Affective Computing**: Analyze the user's facial expression/voice to determine their emotional state. If Happy -> cheerful tone. If Sad -> empathetic tone. If Frustrated/Angry -> slower, clearer explanations.\n\nCRITICAL BEHAVIOR RULES:\n1. DO NOT repeat your introduction or greeting. Just answer the user's current request directly.\n2. If you just executed a tool, tell the user EXACTLY what you just did (e.g., 'I have successfully opened Safari').\n3. You MUST format your final response as a pure JSON object (do not use markdown ```json tags). Format: {\"response\": \"Your spoken text\", \"emotion\": \"neutral/happy/sad/angry/surprised\"}"
    
    content = [
        {"type": "text", "text": "This audio contains my spoken message. Please listen to it, follow any commands I give you, and respond naturally."},
        {"type": "media", "mime_type": "audio/wav", "data": wav_b64}
    ]
    try:
        res = await llm.ainvoke([SystemMessage(content=sys_prompt), HumanMessage(content=content)])
        print("RESULT:", res.content)
    except Exception as e:
        print("ERROR:", e)

asyncio.run(test())
