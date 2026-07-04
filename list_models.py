import asyncio
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def main():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    models = client.models.list()
    for m in models:
        print(f"Model: {m.name}, version: {m.version}")

if __name__ == "__main__":
    main()
