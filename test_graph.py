import asyncio
from app.agents.coordinator import coordinator_graph
from langchain_core.messages import HumanMessage

async def main():
    print("Testing LangGraph...")
    state = {
        "messages": [HumanMessage(content="Hello! Are you there?")],
        "selected_personality": "Professional",
        "user_id": "test",
        "context": ""
    }
    print("Invoking graph...")
    try:
        result = await coordinator_graph.ainvoke(state)
        print("Result:", result["messages"][-1].content)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
