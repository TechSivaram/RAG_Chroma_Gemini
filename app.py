# app.py (Regenerated with adjusted chunking, more results, softened prompt, and debug prints)

import os
import google.generativeai as genai
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- Configuration ---
# Load environment variables from .env file
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("Please set the GOOGLE_API_KEY environment variable in your .env file or directly.")

genai.configure(api_key=GOOGLE_API_KEY)

# Define the path for your ChromaDB persistence
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "pride_and_prejudice_knowledge" # Keep this consistent
KNOWLEDGE_FILE = "data/knowledgebase.txt" # This should point to your large novel file

# --- RAG Parameter Adjustments ---
CHUNK_SIZE = 700  # Adjusted chunk size (potentially more precise)
CHUNK_OVERLAP = 70 # Adjusted overlap
N_RESULTS_RETRIEVAL = 10 # Increased number of retrieved documents
GEMINI_MODEL = 'gemini-1.5-flash'
GEMINI_TEMPERATURE = 0.3 # Temperature allowing for some synthesis

# --- Global/Cached Variables ---
_chroma_collection = None
_gemini_model = None

# --- 1. Load and Process Data (Using LangChain's Text Splitter) ---
def load_and_chunk_document(file_path, chunk_size, chunk_overlap):
    """Loads a text file and splits it into chunks using LangChain's RecursiveCharacterTextSplitter."""
    print(f"Loading and chunking '{file_path}' using RecursiveCharacterTextSplitter with chunk_size={chunk_size}, overlap={chunk_overlap}...")
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_text(text)
    print(f"Text loaded and split into {len(chunks)} chunks.")
    return chunks

# --- 2. Initialize ChromaDB and Embeddings ---
def get_chroma_collection():
    """Initializes and returns the ChromaDB collection (cached)."""
    global _chroma_collection
    if _chroma_collection is None:
        print("Initializing ChromaDB collection...")
        gemini_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=GOOGLE_API_KEY)
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=gemini_ef
        )

        if collection.count() == 0:
            print("Collection is empty. Loading and adding documents...")
            document_chunks = load_and_chunk_document(KNOWLEDGE_FILE, CHUNK_SIZE, CHUNK_OVERLAP)
            if document_chunks:
                ids = [f"doc_{i}" for i in range(len(document_chunks))]
                collection.add(
                    documents=document_chunks,
                    ids=ids
                )
                print(f"Added {len(document_chunks)} chunks to ChromaDB.")
            else:
                print("No document chunks to add.")
        else:
            print(f"ChromaDB collection '{COLLECTION_NAME}' already exists with {collection.count()} documents. Skipping indexing.")
        _chroma_collection = collection
    return _chroma_collection

# --- 3. Retrieval Function ---
def retrieve_relevant_documents(query, collection, n_results=N_RESULTS_RETRIEVAL):
    """Retrieves top_k most similar documents from ChromaDB based on a query."""
    print(f"Retrieving {n_results} relevant documents for query: '{query}'")
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results['documents'][0] if results['documents'] else []

# --- 4. Get Gemini Model Instance ---
def get_gemini_model():
    """Initializes and returns the Gemini model (cached)."""
    global _gemini_model
    if _gemini_model is None:
        print(f"Initializing Gemini model: {GEMINI_MODEL}")
        _gemini_model = genai.GenerativeModel(GEMINI_MODEL)
    return _gemini_model

# --- 5. Main RAG Query Function ---
def ask_rag_question(query):
    """
    Combines retrieval and generation to answer a user query using RAG.
    """
    collection = get_chroma_collection()
    model = get_gemini_model()

    retrieved_docs = retrieve_relevant_documents(query, collection, N_RESULTS_RETRIEVAL)

    # --- Debugging Print for Retrieved Documents ---
    if retrieved_docs:
        print("\n--- Retrieved Documents Sent to LLM (for debugging) ---")
        for i, doc in enumerate(retrieved_docs):
            # Limiting print to first 200 chars for readability in terminal
            print(f"Document {i+1} (Length: {len(doc)}):\n'{doc[:200]}...'")
        print("------------------------------------------")
    else:
        print("\n--- No relevant documents retrieved for this query. ---")
        print("------------------------------------------")
    # --- End Debugging Print ---

    context = "\n".join(retrieved_docs) if retrieved_docs else ""

    # Softened Prompt for better factual adherence and allowing reasonable inference
    prompt = f"""
    You are an AI assistant tasked with answering questions based on the provided text.
    Please use the context below to answer the question thoroughly and accurately.
    If the answer is not available or cannot be reasonably inferred from the provided context,
    you must state clearly and concisely: "I cannot find the answer to that question in the provided information."
    Do not introduce any information that is not present in the context.

    Context:
    {context if context else "No specific context was provided from the knowledge base."}

    Question: {query}

    Answer:
    """

    print("\n--- Sending to Gemini LLM ---")
    # Uncomment for more verbose prompt debugging:
    # print(f"Prompt (first 1000 chars):\n{prompt[:1000]}...")

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=GEMINI_TEMPERATURE
            )
        )
        return response.text
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        return "Sorry, I encountered an error while generating the response."

# --- Main block for initial setup (optional, for direct running/testing) ---
if __name__ == "__main__":
    print("Running app.py directly for initial setup/testing...")
    try:
        collection = get_chroma_collection()
        print(f"RAG system ready with {collection.count()} documents.")

        # Test query for 'Mr. Collins' proposal'
        test_query_proposer = "Who proposes to Elizabeth first?"
        print(f"\nTesting with query: '{test_query_proposer}'")
        response_proposer = ask_rag_question(test_query_proposer)
        print("\n--- Test AI Response ---")
        print(response_proposer)

        test_query_no_info = "What is the capital of France?"
        print(f"\nTesting with query: '{test_query_no_info}' (should say 'cannot find')")
        response_no_info = ask_rag_question(test_query_no_info)
        print("\n--- Test AI Response ---")
        print(response_no_info)

    except Exception as e:
        print(f"Initialization or test query failed: {e}")