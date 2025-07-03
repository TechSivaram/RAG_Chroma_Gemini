# ui_app.py

import streamlit as st
import requests
import time

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:5000" # Where your Flask API is running

st.set_page_config(page_title="RAG Chatbot", page_icon="📚")
st.title("📚 Pride and Prejudice RAG Chatbot")
st.markdown("Ask me anything about Jane Austen's 'Pride and Prejudice'!")

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_ready" not in st.session_state:
    st.session_state.rag_ready = False

# --- Functions to interact with the API ---
@st.cache_data(show_spinner="Checking RAG system status...")
def check_rag_status_api():
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json().get("status") == "ready"
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to RAG API server: {e}. Please ensure 'api_server.py' is running.")
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred while checking RAG status: {e}")
        return False

@st.cache_data(show_spinner="Waiting for RAG system to be ready...")
def wait_for_rag_ready():
    while not check_rag_status_api():
        st.info("RAG system is initializing. This may take a few minutes (especially for the first run with a large knowledge base). Please wait...")
        time.sleep(10) # Wait for 10 seconds before checking again
    st.session_state.rag_ready = True
    st.success("RAG system is ready! You can now ask questions.")


def get_rag_response(query):
    try:
        response = requests.post(f"{API_BASE_URL}/ask", json={"query": query}, timeout=120) # Increased timeout for LLM response
        response.raise_for_status()
        return response.json().get("answer", "Error: No answer received from API.")
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 503:
            st.error("RAG system is still initializing. Please wait a moment and try again.")
        else:
            st.error(f"HTTP error occurred: {http_err} - {response.text}")
        return "An API error occurred."
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the RAG API server. Is 'api_server.py' running?")
        return "Connection error."
    except requests.exceptions.Timeout:
        st.error("The RAG API timed out. The LLM might be taking too long or the server is busy.")
        return "Timeout error."
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return "An unexpected error occurred."

# --- Main UI Logic ---

# Check if RAG is ready or start waiting
if not st.session_state.rag_ready:
    wait_for_rag_ready()

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me about Pride and Prejudice..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get RAG response if system is ready
    if st.session_state.rag_ready:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_rag_response(prompt)
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        with st.chat_message("assistant"):
            st.warning("RAG system is still initializing. Please wait a bit longer before asking questions.")