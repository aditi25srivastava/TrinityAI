import os
from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key starting with: {api_key[:5] if api_key else 'None'}")

try:
    from google.genai import Client
    client = Client(api_key=api_key)
    for m in client.models.list():
        print(m.name)
except Exception as e:
    print("Error:", e)

