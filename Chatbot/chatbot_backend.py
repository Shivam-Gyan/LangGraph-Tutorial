# imports 

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START,END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel, Field
from typing import List, Annotated
from dotenv import load_dotenv
import operator
import os

load_dotenv()


# model setup
model = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.5-flash-lite", temperature=0)

# defining state schema
class ChatBOTState(BaseModel):
    messages: Annotated[List[BaseMessage],add_messages]


# defining graph nodes
def chat_bot(state: ChatBOTState) :
    response = model.invoke(state.messages)
    return {'messages':[response]}

# defining graph 
graph = StateGraph(ChatBOTState)

# adding nodes to graph
graph.add_node("chat_bot",chat_bot)

# defining edges
graph.add_edge(START,"chat_bot")
graph.add_edge("chat_bot",END)

# defining checkpoint saver
checkpoint = InMemorySaver()

# compiling the graph with checkpointing
chatbot = graph.compile(checkpointer = checkpoint)




