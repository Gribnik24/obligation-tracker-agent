from langchain_openrouter.chat_models import ChatOpenRouter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from config.system_prompt import SYSTEM_PROMPT
from config.settings import settings
from src.tools import tools_list

llm = ChatOpenRouter(
    model=settings.MODEL_NAME,
    api_key=settings.MODEL_API_KEY,
    base_url=settings.MODEL_API_BASE,
    temperature=settings.TEMPERATURE
)
memory = MemorySaver()

def make_agent_node(system_prompt: str, tools_list: list):
    llm_with_tools = llm.bind_tools(tools_list, parallel_tool_calls=True)

    def agent_node(state: MessagesState) -> dict:
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    return agent_node

def route_after_agent(state: MessagesState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END

def build_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("agent", make_agent_node(SYSTEM_PROMPT, tools_list))
    builder.add_node("tools", ToolNode(tools_list))
    
    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", route_after_agent)
    builder.add_edge("tools", "agent")
    
    return builder.compile(checkpointer=memory)

agent = build_graph()