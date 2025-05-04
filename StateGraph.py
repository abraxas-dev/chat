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

load_dotenv()
llm_api_key = os.getenv("ANTHROPIC_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}
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

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph_builder.set_finish_point("chatbot")

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}

def stream_graph_updates(user_input: str):
    human_command = Command(resume={"data": user_input})
    events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
    for event in events:
        event["messages"][-1].pretty_print()

while True:
    try:
        user_input = input("\nUser: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        break