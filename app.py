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
    # if "graph" not in st.session_state:
    #     st.session_state.graph, config = create_graph(st.session_state.session_id)

def welcome_page():
    st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
                """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="flex flex-col items-center justify-center min-h-[70vh] px-4 mt-14">
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-center mb-12 text-gray-800">
            Welcome to your AI Assistant
        </h1>
        <h4 class="text-lg md:text-xl lg:text-2xl text-gray-600 text-center mb-12 max-w-2xl">
            I'm your AI assistant. Ask me anything!
        </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    if col2.button("Let's Chat!", key="welcome_button", use_container_width=True):
        st.session_state.started = True
        st.rerun()

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