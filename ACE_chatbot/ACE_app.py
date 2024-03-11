import streamlit as st  # all streamlit commands will be available through the "st" alias
import ACE_lib as glib  # reference to local lib script
from langchain.callbacks import StreamlitCallbackHandler


def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


st.set_page_config(page_title="Ace")  # HTML title
load_css("styles.css")
st.title("Ace - Your Everyday Assistant")  # page title


if 'chat_history' not in st.session_state:  # see if the chat history hasn't been created yet
    st.session_state.chat_history = []  # initialize the chat history

if 'flag' not in st.session_state:
    st.session_state.flag = 0  # Initialize the flag

if 'show_input' not in st.session_state:
    st.session_state.show_input = False  # hidden by default
if 'hide_btn' not in st.session_state:
    st.session_state.hide_btn = False  # shown by default

if 'tech_support_initiated' not in st.session_state:
    st.session_state.tech_support_initiated = False  # Initialize the flag

with st.chat_message("assistant"):
    st.markdown("Hello👋 My name is Ace, how can I assist you today?")


if not st.session_state.hide_btn:
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            btn1 = st.button("Sale Assistant")
            if btn1:
                st.session_state.show_input = True
                st.session_state.hide_btn = True
                st.session_state.flag = 1
                st.session_state.chat_history.append(
                    {"role": "user", "text": "Sale Assistant"})
                st.session_state.chat_history.append(
                    {"role": "assistant", "text": "Ask me anything about the products you are interested in."})
                st.experimental_rerun()

        with col2:
            btn2 = st.button("Tech Support")
            if btn2:
                st.session_state.show_input = True
                st.session_state.hide_btn = True
                st.session_state.flag = 2
                st.session_state.chat_history.append(
                    {"role": "user", "text": "Tech Support"})
                st.session_state.chat_history.append(
                    {"role": "assistant", "text": "What oven model you are facing issues with."})
                st.experimental_rerun()

# Re-render the chat history (Streamlit re-runs this script, so need this to preserve previous chat messages)
for message in st.session_state.chat_history:  # loop through the chat history
    # renders a chat line for the given role, containing everything in the with block
    with st.chat_message(message["role"]):
        st.markdown(message["text"])  # display the chat content


# display a chat input box
input_text = None

if st.session_state.show_input and st.session_state.hide_btn:
    input_text = st.chat_input("Ask Ace...")

if input_text:  # run the code in this if block after the user submits a chat message

    chat_response = None  # initialize the chat response

    with st.chat_message("user"):  # display a user chat message
        st.markdown(input_text)  # renders the user's latest message

    # append the user's latest message to the chat history
    st.session_state.chat_history.append({"role": "user", "text": input_text})

    # use an empty container for streaming output
    st_callback = StreamlitCallbackHandler(st.container())

    if 'memory' not in st.session_state:  # see if the memory hasn't been created yet
        st.session_state.memory = glib.get_memory(
            st_callback, st.session_state.flag)  # initialize the memory

    if st.session_state.flag == 1:
        chat_response = glib.get_chat_response(
            prompt=input_text, memory=st.session_state.memory, streaming_callback=st_callback)

    elif st.session_state.flag == 2:
        # see if the vector index hasn't been created yet
        if 'vector_index' not in st.session_state:
            # show a spinner while the code in this with block runs
            with st.spinner("Indexing document..."):
                # retrieve the index through the supporting library and store in the app's session cache

                try:
                    st.session_state.vector_index = glib.get_index(
                        "pdf/" + input_text + ".pdf")
                    chat_response = st.success(
                        "Document indexed successfully! Please answer any questions you have.")
                except FileNotFoundError:
                    st.error("Document not found. Please try again.")
                    print(FileExistsError)

        else:
            chat_response = glib.get_chat_response_rag(
                prompt=input_text, memory=st.session_state.memory, streaming_callback=st_callback, index=st.session_state.vector_index)

    # append the bot's latest message to the chat history
    st.session_state.chat_history.append(
        {"role": "assistant", "text": chat_response})
