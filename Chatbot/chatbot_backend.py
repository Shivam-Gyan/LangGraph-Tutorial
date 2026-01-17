# imports 

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START,END
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel, Field
from typing import List, Annotated
from dotenv import load_dotenv
import operator
import os
import sqlite3

load_dotenv()


# model setup
# model = ChatGoogleGenerativeAI(api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.5-flash-lite", temperature=0)
model  = ChatOllama(model="ministral-3:3b", temperature=0)

# defining state schema
class ChatBOTState(BaseModel):
    messages: Annotated[List[BaseMessage],add_messages]


# defining graph nodes
def chat_bot(state: ChatBOTState) :
    response = model.invoke(state.messages)
    return {'messages':[response]}


# defining checkpoint saver
# checkpoint = InMemorySaver() # using in-memory saver]
connection = sqlite3.connect("chatbot_checkpoint.db", check_same_thread=False)

checkpoint = SqliteSaver(conn = connection) # using sqlite saver

# defining graph 
graph = StateGraph(ChatBOTState)

# adding nodes to graph
graph.add_node("chat_bot",chat_bot)

# defining edges
graph.add_edge(START,"chat_bot")
graph.add_edge("chat_bot",END)


# compiling the graph with checkpointing
chatbot = graph.compile(checkpointer = checkpoint)


# CONFIG = {
#     "configurable":{
#         "thread_id": "thread_1"
#     }
# }

# initial_state = {
#     'messages':[HumanMessage(content="it's Doe -_- hahahahaha... John Doe") ]
# }

# response = chatbot.invoke(initial_state,config = CONFIG)

# print(response)

# list() is in buitin method of SqliteSaver to list all thread ids and details it is generator 
def get_all_thread_ids():
    threads_details = checkpoint.list(None) #None to get all threads , you can pass specific thread_id to get details of that thread only

    thread_list = set()
    for thread in threads_details:
        thread_list.add(thread.config['configurable']['thread_id'])

    return list(thread_list)

# print(get_all_thread_ids())