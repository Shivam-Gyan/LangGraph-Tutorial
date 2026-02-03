from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage,SystemMessage,BaseMessage
from langgraph.graph.message import add_messages
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_mcp_adapters.client import MultiServerMCPClient

from pydantic import BaseModel
from typing import List,Annotated
import asyncio

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
        }
    }


model = ChatOllama(model="qwen3:1.7b")
# model = ChatOllama(model="deepseek-r1:1.5b") # not support tools 

# search tool 
search_tool = DuckDuckGoSearchRun(region = 'us-en')

# state model for tool input
class ChatState(BaseModel):
    messages: Annotated[List[BaseMessage],add_messages]


# build graph function

async def build_graph():

    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()

    # print(tools)

    # list of tools
    tools = [search_tool] + tools # adding search tool to tools list

    # print(tools) 

    # binding tools with llm
    llm_tools = model.bind_tools(tools)

    # chat node defining
    async def chat_node(state:ChatState):
        messages = state.messages 
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
        'messages':[HumanMessage(content="how many tools i have access?")]
    }

    final_state = await chat_bot.ainvoke(initial_state) # type: ignore

    print(final_state['messages'][-1].content)

if __name__ == "__main__":
    asyncio.run(main())