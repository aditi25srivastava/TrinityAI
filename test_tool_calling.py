import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def dummy_tool(word: str) -> str:
    """Returns the word."""
    return word

models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

for m in models_to_test:
    try:
        print(f"\n--- Testing {m} ---")
        llm = ChatGoogleGenerativeAI(model=m, google_api_key=os.getenv("GEMINI_API_KEY"))
        llm_with_tools = llm.bind_tools([dummy_tool])
        res = llm_with_tools.invoke("Please call the dummy tool with the word 'hello'.")
        print("Response Tool Calls:", res.tool_calls)
    except Exception as e:
        print(f"Error: {e}")
