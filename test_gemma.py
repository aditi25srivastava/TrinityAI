import asyncio
from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage, SystemMessage

async def test():
    llm = OllamaLLM(model="gemma:2b")
    
    system_prompt = """You are Trinity, an AI assistant with the following personality: Professional.
    You are currently running in OFFLINE FALLBACK MODE because the internet is down.
    You MUST respond with a JSON object exactly like this:
    {
        "response": "Your spoken response here",
        "emotion": "neutral"
    }
    Emotions can be: neutral, happy, sad, angry, surprised.
    Do NOT include markdown block formatting, just the raw JSON object.
    """
    
    prompt = "I am offline and didn't hear anything."
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    try:
        res = await llm.ainvoke(messages)
        print("RESULT:", res)
    except Exception as e:
        print("ERROR:", e)

asyncio.run(test())
