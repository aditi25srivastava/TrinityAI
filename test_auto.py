import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

async def test_model(model_name):
    try:
        llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
        response = await llm.ainvoke([HumanMessage(content="Hello")])
        print(f"SUCCESS with {model_name}")
        return True
    except Exception as e:
        print(f"Failed {model_name}: {type(e).__name__} {e}")
        return False

async def main():
    models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp", "gemini-3.5-flash"]
    for m in models:
        await test_model(m)

if __name__ == "__main__":
    asyncio.run(main())
