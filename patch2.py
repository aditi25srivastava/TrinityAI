import re
filepath = "/Users/aditisrivastava/Earner/trinity_ai/venv/lib/python3.14/site-packages/langchain_google_genai/chat_models.py"

with open(filepath, "r") as f:
    content = f.read()

# Let's just find `def _agenerate` since ainvoke calls _agenerate
content = re.sub(r'(async def _agenerate\(.*?\):)', r'\1\n        print("INSIDE _AGENERATE")\n        print(messages)\n', content, flags=re.DOTALL)

with open(filepath, "w") as f:
    f.write(content)
print("Patched again")
