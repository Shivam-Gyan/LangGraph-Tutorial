from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import tools_condition,ToolNode
# from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage,SystemMessage,BaseMessage
from langgraph.graph.message import add_messages
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_mcp_adapters.client import MultiServerMCPClient

from pydantic import BaseModel
from typing import List,Annotated
import asyncio

from dotenv import load_dotenv
import os
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

#  1. model used to generate a structured output according to the plan Schema
# structure_model = ChatOllama(model='qwen3:1.7b',temperature=0.4) 
model = ChatGroq(
    model='qwen/qwen3-32b',
    # model='openai/gpt-oss-120b',
    api_key = GROQ_API_KEY, # type: ignore
    temperature = 0 # Critical for schema adherence
) 

# mcp server 

SERVERS= {
        "expenses_manager": {
        "transport": "stdio",
        "command": "uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            "O:/MCP-tutorial/main.py"
            ]
        },
        # "feather_fables": {
        #     "transport": "streamable_http",
        #     "url": "https://feather-fables-mcp.fastmcp.app/mcp",
        #     "headers": {
        #         "Authorization": "Bearer fmcp_jrM_ztT1u30UAXroQ37SNqXVNpypb6sU8LjutvMbCJo"
        #     }
        # }
        "feather_fables": {
        "transport": "stdio",
        "command": "uv",
        "args": [
            "run",
            "fastmcp",
            "run",
            "O:/feather-fables-mcp/server.py"
            ]
        },
        
    }


# model = ChatOllama(model="qwen3:1.7b")
# model = ChatGroq(model="groq-2:8b")
# model = ChatOllama(model="deepseek-r1:1.5b") # not support tools 

# search tool 
search_tool = DuckDuckGoSearchRun(region = 'us-en') #type: ignore

# state model for tool input
class ChatState(BaseModel):
    messages: Annotated[List[BaseMessage],add_messages]


# build graph function

async def build_graph():

    client = MultiServerMCPClient(SERVERS) #type: ignore
    tools = await client.get_tools()

    # print(tools)

    # list of tools
    tools = [search_tool] + tools # adding search tool to tools list

    # print(tools) 

    # binding tools with llm
    llm_tools = model.bind_tools(tools)

    # chat node defining
    async def chat_node(state:ChatState):
        system_msg = SystemMessage(content=(
            "You are a helpful assistant with access to tools. "
            "When calling a tool, you MUST provide ALL required arguments. "
            "For list_expenses, always provide 'start_date' and 'end_date' in YYYY-MM-DD format. "
            "If the user doesn't specify dates, use a reasonable default range (e.g., 2025-01-01 to 2026-12-31)."
        ))
        messages = [system_msg] + state.messages 
        print("Messages in chat node:",messages)
        response = await llm_tools.ainvoke(messages)
        return {"messages":[response]}

    # tool node defining
    tool_node = ToolNode(tools) # ToolNode have access of each tool added
    
    # creating the instance of StateGraph with state model
    graph = StateGraph(ChatState)

    # add nodes to graph
    graph.add_node('chat_node',chat_node)
    graph.add_node('tools',tool_node) # neccessary to name as it 'tools'

    # add edges to graph
    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges("chat_node",tools_condition) #conditional edges to tools or END
    graph.add_edge("tools","chat_node")

    chat_bot = graph.compile()

    return chat_bot



async def main():
    chat_bot = await build_graph()

    initial_state = {
        'messages':[HumanMessage(content="user this access_token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyYW5kb21faWQiOiI2OTk1ZDFjN2MxNTNmODk3NDkxMTg2YzgiLCJ0b2tlbl9uYW1lIjoiUHJvZHVjdGlvbl9hcGkiLCJ0b2tlbiI6IiQyYiQxMCQ4SnlQbWJZWnZBWmYuUGFxZ0h1azhlVEJwU0h1Zkk3NEI0ZzBjcUNtYWxScXA2VGdOZFVieSIsImV4cGlyeV9kYXlzIjoxNCwiZXhwaXJ5X2RhdGUiOiIyMDI2LTAzLTA1VDEwOjA4OjE1LjIwMVoiLCJpYXQiOjE3NzE0OTU2OTUsImV4cCI6MTc3MjcwNTI5NX0.a-flfKv8gVUeJ8drRSR2kRy0-Zs4JfiRr14xgLlAUwk' to get the profile")]
    }

    final_state = await chat_bot.ainvoke(initial_state) # type: ignore

    print(final_state['messages'][-1].content)

if __name__ == "__main__":
    asyncio.run(main())