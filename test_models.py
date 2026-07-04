import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

models_to_test = [
    "gemini-flash-latest",
    "gemini-2.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3.1-pro-preview",
]

async def main():
    for m in models_to_test:
        print(f"\n--- Testing {m} ---")
        llm = ChatGoogleGenerativeAI(model=m, google_api_key=os.getenv("GEMINI_API_KEY"), max_retries=0)
        try:
            res = await llm.ainvoke([HumanMessage(content="Hello")])
            print("SUCCESS with", m)
        except Exception as e:
            print("ERROR with", m, ":", e)

if __name__ == "__main__":
    asyncio.run(main())
