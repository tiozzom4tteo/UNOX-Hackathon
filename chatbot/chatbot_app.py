import streamlit as st  # all streamlit commands will be available through the "st" alias
import chatbot_lib as glib  # reference to local lib script
from langchain.callbacks import StreamlitCallbackHandler


def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


st.set_page_config(page_title="Ace")  # HTML title
load_css("styles.css")
st.title("Ace - Your Everyday Assistant")  # page title


if 'memory' not in st.session_state:  # see if the memory hasn't been created yet
    st_callback = StreamlitCallbackHandler(st.container())
    st.session_state.memory = glib.get_memory(
        st_callback)  # initialize the memory


if 'chat_history' not in st.session_state:  # see if the chat history hasn't been created yet
    st.session_state.chat_history = []  # initialize the chat history


# Re-render the chat history (Streamlit re-runs this script, so need this to preserve previous chat messages)
for message in st.session_state.chat_history:  # loop through the chat history
    # renders a chat line for the given role, containing everything in the with block
    with st.chat_message(message["role"]):
        st.markdown(message["text"])  # display the chat content


# display a chat input box
input_text = st.chat_input("Ask Ace...")

if input_text:  # run the code in this if block after the user submits a chat message

    with st.chat_message("user"):  # display a user chat message
        st.markdown(input_text)  # renders the user's latest message

    # append the user's latest message to the chat history
    st.session_state.chat_history.append({"role": "user", "text": input_text})

    # use an empty container for streaming output
    st_callback = StreamlitCallbackHandler(st.container())
    chat_response = glib.get_chat_response(
        prompt=input_text, memory=st.session_state.memory, streaming_callback=st_callback)

    # with st.chat_message("assistant"):  # display a bot chat message
    #     st.markdown(chat_response)  # display bot's latest response

    # append the bot's latest message to the chat history
    st.session_state.chat_history.append(
        {"role": "assistant", "text": chat_response})
