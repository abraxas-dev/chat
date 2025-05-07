import streamlit as st
from StateGraph import create_graph, HumanMessage, AIMessage
import uuid
import time
import random

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
    <style>
         @keyframes gradientText {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }
        .gradient-text {
            background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
            background-size: 200% auto;
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientText 6s ease infinite;
        }
        .fade-in {
            animation: fadeIn 1.5s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .stButton > button {
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            color: #6366f1 !important;
            font-weight: bold;
            padding: 0.8em 2em;
            border-radius: 1em;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background: rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.1);
            transform: translateY(-3px);
            color: #8b5cf6 !important;
        }
        
        body {
            background: linear-gradient(135deg, #667eea, #764ba2, #6B8DD6);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }
        
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
    </style>
                """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="flex flex-col items-center justify-center min-h-[70vh] px-4 mt-24">
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-center mb-8 text-gray-800 gradient-text mx-auto text-center">
            Welcome to your AI Assistant
        </h1>
        <h4 class="text-lg md:text-xl lg:text-2xl text-gray-600 text-center mb-12 max-w-2xl gradient-text fade-in text-center">
            I'm your AI assistant. Ask me anything!
        </p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    if col2.button("Let's Chat!", key="welcome_button", use_container_width=True):
        st.session_state.started = True
        st.rerun()

def chat_page():
    # Get API keys from sidebar
    openapi_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    anthropic_api_key = st.sidebar.text_input("Anthropic API Key", type="password")
    tavily_api_key = st.sidebar.text_input("Tavily API Key", type="password")

    # Getter for getting response from LLM's
    def get_response(prompt):
        response = random.choice(["Hello", "Hi", "Hey", "How are you?"])
        for word in response.split():
            yield word + " "
            time.sleep(0.5)

        
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Enter a message..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            response = st.write_stream(get_response(prompt))
        st.session_state.messages.append({"role": "assistant", "content": response})
        

def main():
    init_session()
    if not st.session_state.started:
        welcome_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()