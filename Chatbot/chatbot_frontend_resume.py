import streamlit as st
from chatbot_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid


# --------------- utilities ---------------- #

# dynamic thread id generation function
def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id

# reset chat window function
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id 
    save_current_thread(thread_id)
    st.session_state['chat_history'] = []

# append() current thread_id to threads list function
def save_current_thread(thread_id):
    if thread_id not in st.session_state['threads']:
        st.session_state['threads'].append(thread_id)

# load previous chat history function
def load_chat_history(thread_id):
    st.session_state['thread_id'] = thread_id
    config = {"configurable":{"thread_id":thread_id}}
    return chatbot.get_state(config = config).values['messages']





# ------------------ Configuration ------------------ #

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []
    

# list of all thread_ids
if 'threads' not in st.session_state:
    st.session_state['threads'] = []

# if 'thread_id' not in st.session_state:
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

# after generating the thread id, save it to threads list
save_current_thread(st.session_state['thread_id'])

CONFIG = {
    "configurable":{
        "thread_id": st.session_state['thread_id']
    }
}





# ------------------- Streamlit Side Panel ------------------- #

st.sidebar.title("Chatbot Configuration")

if st.sidebar.button('New Chat'):
    reset_chat()


st.sidebar.subheader('My conversations')
for thread_id in st.session_state['threads']:
    if st.sidebar.button(f"{thread_id}"):
        # st.session_state['thread_id'] = thread_id
        chat_history = load_chat_history(thread_id)

        if not chat_history:
            st.session_state['chat_history'] = []
            continue

        temp_chat_history = []

        for message in chat_history:

            if isinstance(message, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_chat_history.append({'role':role,'content':message.content})
        
        st.session_state['chat_history'] = temp_chat_history





# ------------------- Streamlit Main Panel ------------------- #

st.subheader(f"Chatbot Frontend : Thread ID {st.session_state['thread_id']}")
# add a horizontal line
st.markdown("---")


for message in st.session_state['chat_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input("Type your message here...")


if user_input:

    st.session_state['chat_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.markdown(user_input)

    
    # LLM interaction
    initial_state = {
        'messages':[HumanMessage(content=user_input)]
    }

# Without streaming

    # final_state = chatbot.invoke(initial_state,config = CONFIG)

    # bot_response = final_state['messages'][-1].content

    # st.session_state['chat_history'].append({'role':'assistant','content':bot_response})
    # with st.chat_message('assistant'):
    #     st.markdown(bot_response)

# With streaming

    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk,metadata in chatbot.stream(
                initial_state,
                config = CONFIG,
                stream_mode = 'messages'
            )
        )
    st.session_state['chat_history'].append({'role':'assistant','content':ai_message})



