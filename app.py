import streamlit as st
from StateGraph import create_graph, HumanMessage, AIMessage
import uuid

st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def init_session():
    if "started" not in st.session_state:
        st.session_state.started = False
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "graph" not in st.session_state:
        st.session_state.graph, config = create_graph(st.session_state.session_id)

def welcome_page():
    if st.button("Let's Go!"):
        st.session_state.started = True
        st.experimental_rerun()

def chat_page():
    pass

def main():
    init_session()
    if not st.session_state.started:
        welcome_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()