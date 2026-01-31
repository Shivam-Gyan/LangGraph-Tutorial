from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage,SystemMessage
from langgraph.graph.message import add_messages
from langchain_community.tools import DuckDuckGoSearchRun

from pydantic import BaseModel
from typing import List,Annotated
import asyncio


model = ChatOllama(model="ministral-3:3b")

# search tool 
search_tool = DuckDuckGoSearchRun(region = 'us-en')

# 
# result = search_tool.invoke("today news in ai?")

# print("Search Result:", result)

