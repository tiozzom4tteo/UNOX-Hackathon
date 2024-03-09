import streamlit as st
import chatbot_lib as glib
from langchain.callbacks import StreamlitCallbackHandler


def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


st.set_page_config(page_title="Ace")
# load_css("styles.css")
st.title("Ace - Your Everyday Assistant")

if 'memory' not in st.session_state:
    st_callback = StreamlitCallbackHandler(st.container())
    st.session_state.memory = glib.get_memory(st_callback)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'show_input' not in st.session_state:
    st.session_state.show_input = False  # hidden by default
if 'hide_btn' not in st.session_state:
    st.session_state.hide_btn = False  # shown by default


with st.chat_message("assistant"):
    st.write("Hello👋 My name is Ace, how can I assist you today?")

# Render buttons. When btn3 is clicked, set the show_input flag to True
if not st.session_state.hide_btn:
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            btn1 = st.button("Sale Assistant")
            if btn1:
                st.session_state.hide_btn = True
                st.experimental_rerun()

        with col2:
            btn2 = st.button("Tech Support")
            if btn2:
                st.session_state.hide_btn = True
                st.experimental_rerun()
        with col3:
            btn3 = st.button("Start a conversation")
            if btn3:  # When btn3 is clicked
                st.session_state.show_input = True  # Enable input field
                st.session_state.hide_btn = True
                # force refresh
                st.experimental_rerun()


# Only render the chat input if show_input flag is True
if st.session_state.show_input and st.session_state.hide_btn:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])
    input_text = st.chat_input("Ask Ace...")

    if input_text:
        with st.chat_message("user"):
            st.markdown(input_text)

        st.session_state.chat_history.append(
            {"role": "user", "text": input_text})

        st_callback = StreamlitCallbackHandler(st.container())
        chat_response = glib.get_chat_response(
            prompt=input_text, memory=st.session_state.memory, streaming_callback=st_callback)

        # st.session_state.chat_history.append(
        #     {"role": "assistant", "text": chat_response})
