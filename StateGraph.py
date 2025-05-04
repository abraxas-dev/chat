from typing import TypedDict, Annotated, List, Union
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, add_messages
from dotenv import load_dotenv
import os
from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain.callbacks import StdOutCallbackHandler
from langgraph.types import Command, interrupt 
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.messages.base import BaseMessage

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State, llm_with_tools):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def create_graph(thread_id:str="1"):
    load_dotenv()
    llm_api_key = os.getenv("ANTHROPIC_API_KEY")
    tavily_api_key = os.getenv("TAVILY_API_KEY")

    graph_builder = StateGraph(State)

    llm_call = init_chat_model(
    model="anthropic:claude-3-5-sonnet-latest",
    temperature=0.0,
    api_key=llm_api_key
    )
    tool = TavilySearch(max_results=3, api_key=tavily_api_key)
    tools = [tool]
    llm_with_tools = llm_call.bind_tools(tools)
    tool_node = ToolNode(tools=tools)

    graph_builder.add_node("chatbot", lambda state: chatbot(state, llm_with_tools=llm_with_tools))
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.set_entry_point("chatbot")
    graph_builder.set_finish_point("chatbot")

    memory = MemorySaver()
    return graph_builder.compile(checkpointer=memory), {"configurable": {"thread_id": thread_id}}
