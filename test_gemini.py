import asyncio
from langchain_core.messages import HumanMessage
from app.agents.coordinator import coordinator_graph

async def main():
    state = {
        "messages": [HumanMessage(content=[{"type": "text", "text": "Are you online? Answer yes."}])],
        "selected_personality": "Professional",
        "user_id": "test",
        "context": ""
    }
    result = await coordinator_graph.ainvoke(state)
    print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
