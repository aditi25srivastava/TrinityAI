import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def open_application(app_name: str) -> str:
    """Opens an application on the user's mac."""
    return f"Opened {app_name}"

try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash", 
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        max_retries=0
    )
    llm_with_tools = llm.bind_tools([open_application])
    print("Sending message...")
    
    from langchain_core.messages import SystemMessage, HumanMessage
    sys_prompt = "You are a research assistant and an autonomous AI Agent. You have access to tools that can affect the real world. CRITICAL INSTRUCTION: If the user asks you to perform an action, YOU MUST CALL THE CORRESPONDING TOOL IMMEDIATELY. Do not just talk about it."
    
    res = llm_with_tools.invoke([SystemMessage(content=sys_prompt), HumanMessage(content="Please open the Calculator application on my Mac.")])
    print("Response text:", res.content)
    print("Response tool calls:", res.tool_calls)
except Exception as e:
    print(f"Error: {e}")
