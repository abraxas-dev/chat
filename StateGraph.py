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
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.messages.base import BaseMessage
from pydantic import SecretStr

class State(TypedDict):
    messages: Annotated[list, add_messages]

def chatbot(state: State, llm_with_tools):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def create_graph(api_key:str = None, tavily_api_key:str = None):
    if not api_key:
        raise ValueError("API keys are not provided")
    system_message = """You are a helpful assistant that can answer questions and help with tasks.
    You are able to use the following tools:
    - TavilySearch: to search the web for information"""

    graph_builder = StateGraph(State)
    os.environ["TAVILY_API_KEY"] = tavily_api_key

    llm_call = init_chat_model(
                            model="anthropic:claude-3-5-sonnet-latest",
                            temperature=0.0,
                            api_key=api_key,
    )
    tools = []
    if tavily_api_key:
        tool = TavilySearch(max_results=3)
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
    return graph_builder.compile(checkpointer=memory)

class MessageHandler:
    def __init__(self, thread_id:str = "1", api_key:str = None, tavily_api_key:str = None):
        self.graph = create_graph(api_key, tavily_api_key)
        self.config = {"configurable": {"thread_id": thread_id}}

    def handle_message(self, message: str):
        human_message = HumanMessage(content=message)
        try:    
            response = self.graph.invoke({"messages": [human_message]}, config=self.config)
            if not response["messages"]:
                raise ValueError("No response from graph")
            last_message = response["messages"][-1]
            if isinstance(last_message, AIMessage) and last_message.content:
                return last_message.content
            else:
                raise ValueError("Last message is not an AIMessage")

        except Exception as e:
            raise ValueError(f"Error: {e}")
    
    def get_history(self):
        try:
            state = self.graph.get_state(config=self.config)
            return state.get("messages", [])
        except Exception as e:
            raise ValueError(f"Error: {e}")

    def clear_history(self):
        self.graph.reset(config=self.config)