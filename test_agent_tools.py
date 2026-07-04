import asyncio
from app.agents.coordinator import coordinator_graph
from langchain_core.messages import HumanMessage

async def main():
    state = {
        "messages": [HumanMessage(content="Open the Safari application.")],
        "selected_personality": "Professional",
        "user_id": "test_user",
        "context": ""
    }
    print("Invoking graph...")
    result = await coordinator_graph.ainvoke(state)
    print("Messages:")
    for m in result["messages"]:
        print(type(m).__name__, ":", m.content)

if __name__ == "__main__":
    asyncio.run(main())
