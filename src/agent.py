from langchain_gigachat.chat_models import GigaChat
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode

from config.system_prompt import SYSTEM_PROMPT
from config.settings import settings
from tools import tools_list

giga = GigaChat(
    credentials=settings.GIGACHAT_API_KEY,
    model=settings.GIGACHAT_MODEL_NAME,
    temperature=settings.TEMPERATURE,
    verify_ssl_certs=False
)
memory = MemorySaver()

def make_agent_node(system_prompt: str, tools_list: list):
    llm_with_tools = giga.bind_tools(tools_list, parallel_tool_calls=True)

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