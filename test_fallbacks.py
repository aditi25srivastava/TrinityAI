import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def dummy_tool():
    """Dummy tool"""
    pass

primary = ChatGoogleGenerativeAI(model="gemini-1.5-flash-invalid", google_api_key=os.getenv("GEMINI_API_KEY"), max_retries=0)
fallback = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=os.getenv("GEMINI_API_KEY"), max_retries=0)

llm = primary.with_fallbacks([fallback])

try:
    llm_with_tools = llm.bind_tools([dummy_tool])
    res = llm_with_tools.invoke("Hello")
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
