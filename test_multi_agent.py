import asyncio
from langchain_core.messages import HumanMessage
from app.agents.coordinator import supervisor_node

async def test_supervisor(message_text: str):
    state = {
        "messages": [HumanMessage(content=[{"type": "text", "text": message_text}])],
        "selected_personality": "Professional",
        "user_id": "test_user",
        "context": "",
        "next": ""
    }
    result = await supervisor_node(state)
    print(f"Message: '{message_text}' -> Routed to: {result['next']}")

async def main():
    print("Testing Multi-Agent Routing...\n")
    await test_supervisor("How do I reverse a linked list in Python?")
    await test_supervisor("Can we do a mock interview for a software engineering role?")
    await test_supervisor("Please summarize the latest research on quantum computing.")
    await test_supervisor("Could you review my resume and help me network?")

if __name__ == "__main__":
    asyncio.run(main())
