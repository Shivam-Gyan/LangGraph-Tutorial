import streamlit as st
from chatbot_backend import chatbot
from langchain_core.messages import HumanMessage


st.title("Chatbot Frontend")
CONFIG = {
    "configurable":{
        "thread_id":"chat_thread_1"
    }
}


if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []


for message in st.session_state['chat_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input("Type your message here...")

if user_input:

    # display user message
    st.session_state['chat_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    
    # LLM interaction
    initial_state = {
        'messages':[HumanMessage(content=user_input)]
    }

    final_state = chatbot.invoke(initial_state,config = CONFIG)

    bot_response = final_state['messages'][-1].content

    st.session_state['chat_history'].append({'role':'assistant','content':bot_response})
    with st.chat_message('assistant'):
        st.markdown(bot_response)



