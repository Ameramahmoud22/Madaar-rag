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

    try:
        # Load the FAISS vector store for this user only
        vectorstore = FAISS.load_local(
            folder_path=vectorstore_path,
            embeddings=OpenAIEmbeddings(),
            # must be added to upload FAISS vectorstore
            allow_dangerous_deserialization=True
        )


        # Initialize the language model [chatgpt 3.5 turbo]
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

        # Create a RetrievalQA chain [which ask pdf first then ask llm]
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
            return_source_documents=False)

        # Get the response from the chain [ask question then answer]
        response = qa_chain.run(query)
        return response

    except Exception as e:
        return f"An error occurred while processing your request: {str(e)}"
