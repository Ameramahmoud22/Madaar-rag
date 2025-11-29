import os
import asyncio
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFacePipeline
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, pipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


async def get_rag_response(user, query):
    """
    Handles the entire RAG process using local Hugging Face models.
    """
    vectorstore_path = f'vectorstores/{user.username}_vectorstore'

    if not os.path.exists(vectorstore_path):
        return "No documents found for this user, please upload PDFs first."

    def load_vectorstore():
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return FAISS.load_local(
            folder_path=vectorstore_path,
            embeddings=embeddings,
            allow_dangerous_deserialization=True,
        )

    try:
        vectorstore = await asyncio.to_thread(load_vectorstore)
    except Exception as e:
        return f"Failed to load vectorstore: {e}"

    def search_documents():
        return vectorstore.similarity_search(query, k=4)

    try:
        docs = await asyncio.to_thread(search_documents)
    except Exception as e:
        return f"Search failed: {e}"

    context = "\n\n".join(doc.page_content for doc in docs).strip()
    if not context:
        return "No relevant information was found in the uploaded documents."

    prompt_text = (
        "Answer the question using ONLY the context below. If the answer is not in the context, say you don't know.\n\n"
        f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    )

    def setup_and_invoke_llm():
        """Sets up the local LLM pipeline and runs inference."""
        # Define the local model to use for text generation
        model_id = "google/flan-t5-small"

        # Load the tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

        # Create a text-generation pipeline
        pipe = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=256  # Controls the max length of the generated answer
        )

        # Wrap the pipeline in a LangChain object
        llm = HuggingFacePipeline(pipeline=pipe)

        # Invoke the model and return the string response
        return llm.invoke(prompt_text)

    try:
        # Run the entire blocking LLM setup and inference in a background thread
        answer = await asyncio.to_thread(setup_and_invoke_llm)
    except Exception as e:
        # Log the full error for debugging
        print(f"LLM Exception: {e}")
        return f"LLM failure: {e}"

    return (answer or "").strip()
