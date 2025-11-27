import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.chains import RetrievalQA


# Function called from websocket it take [user , question] and and return response from the user's pdf
def get_rag_response(user, query):

    # the path we save on it the vectorstore for each user
    vectorstore_path = f'vectorstores/{user.username}_vectorstore'

    # check if the user has uploaded documents
    if not os.path.exists(vectorstore_path):
        return "No documents found for this user, please upload PDFs first."

    # Load the FAISS vector store for this user only
    vectorstore = FAISS.load_local(
        folder_path=vectorstore_path,
        embeddings=OpenAIEmbeddings(),
        # must be added to upload FAISS vectorstore
        allow_dangerous_deserialization=True
    )

 # Create a retriever from the vector store
    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 3})

    # Initialize the language model [chatgpt 3.5 turbo]
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
