import os
import json
from typing import TypedDict, Annotated, Sequence, Literal
import operator
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from app.core.config import settings
from app.agents.tools import ALL_TOOLS
from app.agents.memory import memory_db

# State definition for the Multi-Agent Graph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    selected_personality: str
    user_id: str
    context: str
    next: str

def init_llm():
    # Primary model is gemini-flash-latest, falling back to other known-good models
    primary = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=settings.GEMINI_API_KEY, max_retries=1)
    fallback_1 = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.GEMINI_API_KEY, max_retries=1)
    fallback_2 = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", google_api_key=settings.GEMINI_API_KEY, max_retries=1)
    return primary.with_fallbacks([fallback_1, fallback_2])

# --- Supervisor ---
class RouterDecision(BaseModel):
    next: Literal["coding", "research", "career", "interview"]

async def supervisor_node(state: AgentState):
    """Analyzes the user request and decides which specialized agent should handle it."""
    llm = init_llm()
    router_llm = llm.with_structured_output(RouterDecision)
    
    last_msg = state['messages'][-1].content
    if isinstance(last_msg, list):
        last_text = " ".join([block.get("text", "") for block in last_msg if block.get("type") == "text"])
    else:
        last_text = str(last_msg)
        
    system_prompt = (
        "You are a Supervisor AI. Route the user's request to the correct specialized agent.\n"
        "Agents:\n"
        "- coding: For software engineering, coding questions, debugging, algorithms.\n"
        "- research: For searching the web, analyzing documents/notes, factual lookups, general questions.\n"
        "- career: For resume building, networking, career advice.\n"
        "- interview: For mock interviews, behavioral questions, feedback.\n\n"
        "If you don't know, default to 'research'."
    )
    
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=last_text)]
    try:
        decision = await router_llm.ainvoke(messages)
        next_agent = decision.next
    except Exception as e:
        print(f"Supervisor parsing failed, defaulting to research: {e}")
        next_agent = "research"
    
    print(f"Supervisor routed request to: {next_agent.upper()} AGENT")
    return {"next": next_agent}

# --- Specialized Agents (Workers) ---

def make_agent(role: str, specialty: str):
    def prompt_builder(state: AgentState) -> str:
        messages = state['messages']
        last_msg = messages[-1].content
        if isinstance(last_msg, list):
            last_text = " ".join([block.get("text", "") for block in last_msg if block.get("type") == "text"])
        else:
            last_text = str(last_msg)
            
        user_id = state.get('user_id', 'default_user')
        selected_personality = state.get('selected_personality', 'Professional')
        context = state.get('context', '')
        
        # Save memory
        memory_db.save_memory(last_text, user_id=user_id)
        past_memories = memory_db.get_relevant_memories(last_text, user_id=user_id)
        
        prompt = (
            f"You are the {role} and an autonomous AI Agent.\n"
            f"Your specialty: {specialty}\n\n"
            f"CRITICAL INSTRUCTION: If the user asks you to perform an action, call the corresponding tool immediately.\n\n"
            f"Personality: {selected_personality}. Context: {context}. Past Memories: {past_memories}.\n"
            f"**Affective Computing**: Analyze the user's expression/voice to determine emotional state. Adapt your tone.\n\n"
            f"CRITICAL BEHAVIOR RULES:\n"
            f"1. DO NOT repeat your introduction or greeting. Just answer the user's current request directly.\n"
            f"2. MUST narrate tool usage in spoken text. (e.g. 'Opening Safari')\n"
            f"3. You have a Knowledge Base containing PDFs/notes. Use search_knowledge_base tool if asked about them.\n"
            f"4. You MUST format your final response as a pure JSON object. Format: {{\"response\": \"Your spoken text\", \"emotion\": \"neutral/happy/sad/angry/surprised\", \"satisfaction_score\": 8.5, \"success_rate\": 1.0}}\n"
            f"   - satisfaction_score (0-10): Rate how well you believe you satisfied the user's intent.\n"
            f"   - success_rate (0-1.0): 1.0 if you fully answered the question or completed the tool action, 0 if you failed or couldn't."
        )
        return prompt
        
    return create_react_agent(init_llm(), tools=ALL_TOOLS, prompt=prompt_builder)

coding_agent = make_agent("Coding Agent", "Expert in software engineering, algorithms, system design, and debugging.")
research_agent = make_agent("Research Agent", "Expert in deep analysis, summarizing documents, data synthesis, and factual lookups.")
career_agent = make_agent("Career Agent", "Expert in resume building, career trajectories, and networking strategies.")
interview_agent = make_agent("Interview Agent", "Expert in conducting mock interviews, behavioral questions, and providing constructive feedback.")

# Node Wrappers to safely extract new messages
async def run_coding(state: AgentState):
    result = await coding_agent.ainvoke(state)
    return {"messages": result['messages'][len(state['messages']):]}

async def run_research(state: AgentState):
    result = await research_agent.ainvoke(state)
    return {"messages": result['messages'][len(state['messages']):]}

async def run_career(state: AgentState):
    result = await career_agent.ainvoke(state)
    return {"messages": result['messages'][len(state['messages']):]}

async def run_interview(state: AgentState):
    result = await interview_agent.ainvoke(state)
    return {"messages": result['messages'][len(state['messages']):]}

# --- Graph Definition ---
def build_multi_agent_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("coding", run_coding)
    workflow.add_node("research", run_research)
    workflow.add_node("career", run_career)
    workflow.add_node("interview", run_interview)
    
    workflow.set_entry_point("supervisor")
    
    # Conditional routing from supervisor to workers
    workflow.add_conditional_edges(
        "supervisor",
        lambda x: x["next"],
        {
            "coding": "coding",
            "research": "research",
            "career": "career",
            "interview": "interview"
        }
    )
    
    # All workers route to END
    workflow.add_edge("coding", END)
    workflow.add_edge("research", END)
    workflow.add_edge("career", END)
    workflow.add_edge("interview", END)
    
    return workflow.compile()

coordinator_graph = build_multi_agent_graph()

