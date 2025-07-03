# api_server.py

from flask import Flask, request, jsonify
from app import ask_rag_question # Import the core RAG function from app.py
import os
import threading

app = Flask(__name__)

# A flag to indicate if the RAG system is ready
rag_system_ready = False
rag_init_lock = threading.Lock()

def initialize_rag_system():
    """Initializes the RAG system in a separate thread."""
    global rag_system_ready
    with rag_init_lock:
        if not rag_system_ready:
            print("--- Initializing RAG system (may take a while)... ---")
            try:
                # Call a function from app.py that triggers ChromaDB loading/indexing
                from app import get_chroma_collection
                get_chroma_collection()
                rag_system_ready = True
                print("--- RAG system initialized and ready! ---")
            except Exception as e:
                print(f"--- RAG system initialization FAILED: {e} ---")
                # You might want to handle this more robustly, e.g., exit or retry
                os._exit(1) # Exit the process if initialization fails


@app.before_request
def check_rag_status():
    global rag_system_ready
    if not rag_system_ready:
        if not rag_init_lock.locked():
            # Start initialization in a separate thread if not already running
            print("Starting RAG system initialization in background...")
            threading.Thread(target=initialize_rag_system).start()
        # Return a temporary message while initializing
        return jsonify({"message": "RAG system is initializing. Please try again in a moment."}), 503 # Service Unavailable


@app.route('/ask', methods=['POST'])
def ask():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    print(f"Received query via API: '{query}'")
    response_text = ask_rag_question(query)
    print(f"Sending response via API: '{response_text[:100]}...'")

    return jsonify({"answer": response_text})

@app.route('/status', methods=['GET'])
def status():
    global rag_system_ready
    if rag_system_ready:
        return jsonify({"status": "ready", "message": "RAG system is fully initialized and operational."})
    else:
        return jsonify({"status": "initializing", "message": "RAG system is currently loading knowledge base and embeddings. Please wait."})

if __name__ == '__main__':
    # Start initialization in a separate thread immediately
    threading.Thread(target=initialize_rag_system).start()
    print("Flask API starting on http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)