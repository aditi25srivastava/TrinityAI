import os

filepath = "/Users/aditisrivastava/Earner/trinity_ai/venv/lib/python3.14/site-packages/langchain_google_genai/chat_models.py"

with open(filepath, "r") as f:
    content = f.read()

patch_code = """
        print("====== SENDING TO GOOGLE ======")
        for req in requests:
            print(req)
        print("===============================")
"""
# Find where the generate_content is called.
# It's usually `self.client.models.generate_content(` or `self.client.generate_content(`
# Let's just find `def _generate`
import re
new_content = re.sub(r'(def _generate\(.*?:\n)', r'\1        print("INSIDE _GENERATE")\n        print(messages)\n', content, flags=re.DOTALL)

with open(filepath, "w") as f:
    f.write(new_content)
print("Patched chat_models.py")
