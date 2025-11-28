import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Function called from websocket it take [user , question] and and return response from the user's pdf



def get_rag_response(user, query):

    # the path we save on it the vectorstore for each user
    vectorstore_path = f'vectorstores/{user.username}_vectorstore'

    # check if the user has uploaded documents
    if not os.path.exists(vectorstore_path):
        return "No documents found for this user, please upload PDFs first."

    try:
        # Load the FAISS vector store for this user only
        vectorstore = FAISS.load_local(
            folder_path=vectorstore_path,
            embeddings=OpenAIEmbeddings(),
            # must be added to upload FAISS vectorstore
            allow_dangerous_deserialization=True
        )
         # retieve the top 4 relevant documents from the vectorstore[pdf]
        docs = vectorstore.similarity_search(query, k=4)
        # combine the content of the retrieved documents
        context = "\n\n".join([doc.page_content for doc in docs])

        if not context.strip():
            return "No relevant information found in the uploaded documents."
        
        # Initialize the language model [chatgpt 3.5 turbo] => ask chatgpt directly
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
 
        # Create a prompt template with context and question
        prompt = f"""Answer the following question using only the provided context from the user's uploaded PDF.
                   Be concise and do not add any information not present in the context.

Context:
{context}

Question: {query}

Answer:"""

        response = llm.invoke(prompt)
        return response.content.strip()
       

    except Exception as e:
        return f"An error occurred while processing your request: {str(e)}"
