# Local RAG Chat with Django and WebSockets

This project is a self-contained Retrieval-Augmented Generation (RAG) chat application built with Django. It allows users to upload PDF documents and ask questions about their content. The entire process, from document analysis to answer generation, runs on your local machine using open-source Hugging Face models, ensuring privacy and eliminating the need for external API keys.

## Features

- **Token-Based Authentication:** Secure endpoints protected by user-specific authentication tokens.
- **PDF Upload & Processing:** Upload PDF files via a REST API endpoint. The text is automatically extracted, chunked, and indexed into a local vector store.
- **Real-Time Chat via WebSockets:** Engage in a real-time conversation with the RAG system through a WebSocket connection.
- **100% Local AI:** Both the document embedding model (`all-MiniLM-L6-v2`) and the language generation model (`google/flan-t5-small`) run locally.
- **Asynchronous Django:** Built with Django Channels to handle WebSocket connections and asynchronous operations efficiently.

---

## Architecture

The application follows a classic Django setup extended with `Django Channels` for WebSocket support.

1.  **Backend Framework:** `Django` serves as the primary web framework, managing user authentication and handling API requests.
2.  **Authentication:** `djangorestframework-authtoken` provides a simple token-based authentication system. A user logs in via a standard API endpoint and receives a token.
3.  **API Endpoints:**
    - `/api/login/`: Authenticates a user and returns an auth token.
    - `/api/upload/`: A protected endpoint for uploading PDF files. It uses `PyPDF2` to extract text.
4.  **Text Processing & Storage:**
    - **Text Splitting:** `langchain`'s text splitters break the extracted text into manageable chunks.
    - **Embeddings:** `HuggingFaceEmbeddings` (using the `all-MiniLM-L6-v2` model) converts text chunks into numerical vectors.
    - **Vector Store:** `FAISS` (from Meta AI) is used to create a local, efficient, and searchable vector store. The store for each user is saved in the `vectorstores/` directory.
5.  **WebSocket Chat (`/ws/chat/`):**
    - `Django Channels` manages the WebSocket lifecycle.
    - The connection is authenticated using the token provided in the WebSocket URL.
    - When a query is received, the application searches the user's FAISS vector store for relevant document chunks.
    - The query and the retrieved context are passed to a local `HuggingFacePipeline` (using the `google/flan-t5-small` model) which generates the final answer.
    - The response is streamed back to the client word-by-word.

---

## Setup and Installation

Follow these steps to set up and run the project on your local machine.

**Prerequisites:**

- Python 3.8+
- A virtual environment tool (`venv`)

**1. Clone the Repository:**

```bash
git clone <your-repo-url>
cd <your-project-directory>
```

**2. Create and Activate a Virtual Environment:**

```bash
# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies:**

All required Python packages are listed in `requirements.txt`. Install them using pip:

```bash
pip install -r requirements.txt
```

**4. Run Django Migrations:**

This will set up the necessary database tables for users and authentication tokens.

```bash
python manage.py migrate
```

**5. Create a Superuser:**

You need a user account to test the application. Create one using the command below and follow the prompts.

```bash
python manage.py createsuperuser
```

**6. Start the Django Server:**

```bash
python manage.py runserver
```

The server will start, and the application will be ready. The first time you ask a question, the `flan-t5-small` model (approx. 300MB) will be downloaded. This is a one-time process and may take a few minutes.

---

## Dependencies and Environment Variables

### Dependencies

All Python dependencies required to run this project are listed in the `requirements.txt` file. Key libraries include:

- `Django` & `djangorestframework`
- `channels` for WebSocket support
- `langchain`, `langchain-huggingface` for the RAG pipeline
- `transformers` and `torch` for running local Hugging Face models
- `sentence-transformers` for embeddings
- `faiss-cpu` for the vector store
- `PyPDF2` for PDF text extraction

### Environment Variables

**This project does not require any environment variables or API keys.**

Since all models (for both embeddings and language generation) are open-source and run locally, there is no need to configure external services like OpenAI. All processing is handled on your own machine.

---

## How to Use the Application

Interact with the application using an API client (like Postman, Insomnia, or a script).

**1. Get Your Authentication Token:**

Send a POST request to the login endpoint with your superuser credentials.

- **URL:** `http://127.0.0.1:8000/api/login/`
- **Method:** `POST`
- **Body (JSON):**
  ```json
  {
    "username": "your-username",
    "password": "your-password"
  }
  ```

**Response:**

```json
{
  "token": "your_auth_token_string"
}
```

**2. Upload a PDF:**

Send a POST request to the upload endpoint. This is a multipart form data request.

- **URL:** `http://127.0.0.1:8000/api/upload/`
- **Method:** `POST`
- **Headers:**
  - `Authorization`: `Token your_auth_token_string`
- **Body (form-data):**
  - Key: `file`
  - Value: Select your PDF file.

**3. Connect to the WebSocket and Chat:**

Connect to the WebSocket endpoint using a WebSocket client (like the included `websocket_tester.py` script).

- **URL:** `ws://127.0.0.1:8000/ws/chat/?token=your_auth_token_string`

Once connected, you can send JSON messages with your questions:

```json
{
  "query": "What is the main topic of the document?"
}
```

The server will respond with a series of messages, including `thinking`, `stream` (for each word), and `done`.
