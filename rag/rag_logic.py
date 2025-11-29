from multiprocessing import context
import os
import asyncio
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from regex import search

# Function called from websocket it take [user , question] and and return response from the user's pdf


async def get_rag_response(user, query):

    # the path we save on it the vectorstore for each user
    vectorstore_path = f'vectorstores/{user.username}_vectorstore'

    # check if the user has uploaded documents
    if not os.path.exists(vectorstore_path):
        return "No documents found for this user, please upload PDFs first."

    # Load the FAISS vector store for this user only
    def load_vs():
        return FAISS.load_local(
            folder_path=vectorstore_path,
            embeddings=OpenAIEmbeddings(),
            allow_dangerous_deserialization=True,
        )
    try:
        vs = await asyncio.to_thread(load_vs)
    except Exception as e:
        return f"Failed to load vectorstore: {e}"

        # retieve the top 4 relevant documents from the vectorstore[pdf]
    def search():
        return vs.similarity_search(query, k=4)

    try:
        docs = await asyncio.to_thread(search)
    except Exception as e:
        return f"Search failed: {e}"

    context = "\n\n".join(getattr(d, "page_content", str(d))
                          for d in docs).strip()
    if not context:
        return "No relevant information found in the uploaded documents."
        # Create a prompt template with context and question
    prompt = (
        "Answer the question using ONLY the context below. If the answer is not in the context, say you don't know.\n\n"
        f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:"
    )

    # Initialize the language model [chatgpt 3.5 turbo] => ask chatgpt directly
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

    def call_llm():
        # prefer predict if available; fall back to calling object
        try:
            return llm.predict(prompt)
        except Exception:
            res = llm(prompt)
            return getattr(res, "content", getattr(res, "text", str(res)))

    try:
        answer = await asyncio.to_thread(call_llm)
    except Exception as e:
        return f"LLM failure: {e}"

    return (answer or "").strip()
