# 📚 RAG Chatbot with Google Gemini and ChromaDB (Pride and Prejudice Edition)

## Project Overview

This project implements a Retrieval-Augmented Generation (RAG) chatbot using Google's Gemini LLM (Large Language Model) and ChromaDB as a vector store. The chatbot's knowledge base is currently Jane Austen's classic novel, "Pride and Prejudice," allowing it to answer questions specifically about the book's characters, plot, and settings.

The application consists of a backend API (Flask) that handles the core RAG logic (embedding, retrieval, and LLM generation) and a frontend UI (Streamlit) for user interaction.

## Features

* **RAG Architecture:** Leverages RAG to ground LLM responses in a specific knowledge base, reducing hallucination.
* **Google Gemini Integration:** Uses Google's Gemini models for powerful text generation and embeddings.
* **ChromaDB Vector Store:** Efficiently stores and retrieves text chunks based on semantic similarity.
* **Intelligent Chunking:** Employs LangChain's `RecursiveCharacterTextSplitter` for better context preservation during document processing.
* **Flexible UI:** An interactive web interface built with Streamlit for easy questioning.
* **RESTful API:** A Flask-based API endpoint for programmatic access to the RAG functionality.
* **Asynchronous Initialization:** The RAG system initializes in a background thread to keep the API responsive during the initial (potentially long) indexing process.

## Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.8+**
* **pip** (Python package installer)
* **Git**

## Setup Instructions

### 1. Clone the Repository

First, clone this Git repository to your local machine:

    git clone <your-repository-url>
    cd <your-repository-name> # e.g., cd rag_app

### 2. Set Up Virtual Environment (Recommended)

It's highly recommended to use a virtual environment to manage project dependencies:

    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate

### 3. Install Dependencies

Install all required Python packages using the `requirements.txt` file:

    pip install -r requirements.txt

### 4. Obtain Google Gemini API Key

You need a Google Gemini API key to use the Gemini models for embeddings and generation.

1.  Go to the [Google AI Studio](https://aistudio.google.com/app/apikey) website.
2.  Log in with your Google account.
3.  Click "Create API key in new project" or "Get API key".
4.  Copy your API key.

### 5. Configure API Key

Create a file named `.env` in the root directory of your project (`rag_app/`). Add your API key to this file:

    # .env
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"

Replace `"YOUR_GEMINI_API_KEY_HERE"` with the actual API key you copied.

### 6. Prepare the Knowledge Base

The project uses "Pride and Prejudice" as its knowledge base.

1.  **Download the text file:**
    * Go to [Project Gutenberg](https://www.gutenberg.org/ebooks/1342) (Pride and Prejudice page).
    * Look for the "Plain Text UTF-8 (without Byte Order Mark)" download link.
    * Download the file.
2.  **Place the file:**
    * Create a directory named `data` in your project root (`rag_app/data/`).
    * Rename the downloaded text file to `knowledgebase.txt` and place it inside the `data` directory.

Your project structure should now look like this:

    rag_app/
    ├── data/
    │   └── knowledgebase.txt
    ├── .env
    ├── app.py
    ├── api_server.py
    ├── ui_app.py
    └── requirements.txt

### 7. Clear ChromaDB Cache (Important for first run or data changes)

ChromaDB caches embeddings locally. Whenever you change the `knowledgebase.txt` file or modify the `CHUNK_SIZE`/`CHUNK_OVERLAP` parameters in `app.py`, you **must** delete the existing ChromaDB data to force a re-indexing.

    # On Windows PowerShell:
    Remove-Item -Path .\chroma_db -Recurse -Force

    # On Windows Command Prompt (CMD):
    rmdir /s /q chroma_db

    # On macOS/Linux:
    rm -rf chroma_db

## Running the Application

You need to run the API server and the UI application in separate terminal windows.

### 1. Start the API Server

Open your first terminal, navigate to the project root, activate your virtual environment, and run the Flask API server:

    # Ensure virtual environment is activated
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate

    python api_server.py

The API server will start, typically on `http://127.0.0.1:5000`. You will see messages about the RAG system initializing. This process (chunking and embedding the novel) will take several minutes on the first run. The API will return a `503 Service Unavailable` status until it's ready.

### 2. Start the UI Application

Open a second terminal, navigate to the project root, activate your virtual environment, and run the Streamlit UI:

    # Ensure virtual environment is activated
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate

    streamlit run ui_app.py

This will open a new tab in your web browser, typically at `http://localhost:8501`. The UI will display a message indicating that the RAG system is initializing.

## Usage

1.  **Wait for Initialization:** Both the API and UI will show messages about the RAG system initializing. Please wait until the API terminal indicates "--- RAG system initialized and ready! ---" and the Streamlit UI shows "RAG system is ready! You can now ask questions." This could take several minutes for the first indexing of "Pride and Prejudice."
2.  **Ask Questions:** Once ready, type your questions about "Pride and Prejudice" into the chat input field in the Streamlit UI.
    * **Examples:**
        * "Who is Elizabeth Bennet?"
        * "What is the name of Mr. Darcy's estate?"
        * "Who proposes to Elizabeth first?" (Test this one!)
        * "Describe Jane Bennet's personality."
        * "What happened at the Netherfield ball?"
        * "What are the names of the Bennet sisters?"
3.  **Observe Responses:** The chatbot will provide answers based on the novel's content. If the information isn't found in the knowledge base, it will explicitly state that.

## Project Structure

    rag_app/
    ├── data/
    │   └── knowledgebase.txt   # The novel "Pride and Prejudice" text file
    ├── .env                    # Environment variables (e.g., GOOGLE_API_KEY)
    ├── app.py                  # Core RAG logic (chunking, embedding, retrieval, LLM interaction)
    ├── api_server.py           # Flask API to expose RAG functionality
    ├── ui_app.py               # Streamlit web interface for the chatbot
    ├── requirements.txt        # Python dependencies
    ├── chroma_db/              # Directory for ChromaDB persistence (created on first run)
    └── README.md               # This file

## Troubleshooting

* **"A positional parameter cannot be found that accepts argument '/q'"**: You are likely running a Windows CMD command (`rmdir /s /q`) in PowerShell. Use `Remove-Item -Path .\chroma_db -Recurse -Force` instead for PowerShell.
* **"I cannot find the answer to that question..."**:
    * **Check retrieved chunks:** Look at the `api_server.py` terminal output. Do the "Retrieved Documents Sent to LLM" contain the answer or related context?
    * If not, the issue is **retrieval**. Try adjusting `CHUNK_SIZE`, `CHUNK_OVERLAP` in `app.py`, then **delete `chroma_db` and restart both servers**. Experiment with different values (e.g., smaller chunks like `CHUNK_SIZE=500`, `CHUNK_OVERLAP=50`).
    * If yes, the issue is **generation**. The LLM might be too strict. Re-examine the prompt in `app.py` or slightly increase `GEMINI_TEMPERATURE` (e.g., to `0.4` or `0.5`).
* **API/UI "Initializing..." forever:**
    * Ensure your `GOOGLE_API_KEY` in `.env` is correct.
    * Verify `knowledgebase.txt` is in `data/` and not empty.
    * Check for any error messages in the terminal where `api_server.py` is running.
    * Confirm you deleted `chroma_db` if it's the first run or after changing chunking parameters.
* **"Could not connect to RAG API server..."**: Ensure `api_server.py` is running successfully in a separate terminal before starting `ui_app.py`.

## Future Enhancements

* **Advanced Chunking:** Explore more sophisticated chunking strategies (e.g., semantic chunking, or using LangChain's document loaders for structured data).
* **Hybrid Search:** Combine vector similarity search with keyword-based search for improved retrieval.
* **Query Expansion/Re-ranking:** Use an LLM to generate multiple relevant queries or re-rank retrieved documents for better context.
* **Error Handling and Logging:** More robust error handling and detailed logging for production environments.
* **User Feedback:** Implement a mechanism for users to provide feedback on answer quality.
* **Deployment:** Deploy the application to a cloud platform (e.g., Render, Streamlit Community Cloud, Google Cloud Run) using Docker for containerization and a reverse proxy for unified URLs.
* **Broader Knowledge Base:** Allow users to upload their own documents or integrate with other data sources.

---

## License

This project is open-source and available under the MIT License.

## Screen Shots

<img width="1271" alt="image" src="https://github.com/user-attachments/assets/1e63a2a2-21c8-4c24-9df9-a5e7e01399ff" />

<img width="1240" alt="image" src="https://github.com/user-attachments/assets/fc4ae362-da8f-4909-a33d-6e5949d7fc17" />

<img width="1275" alt="image" src="https://github.com/user-attachments/assets/fab4a0c1-ea7b-4071-a58d-432525dad16b" />




