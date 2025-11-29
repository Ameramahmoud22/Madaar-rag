import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
from django.contrib.auth import authenticate
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# Login view


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        return Response({'error': 'Invalid Credentials'}, status=400)


# Upload pdf view


class UploadPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        if not file.name.lower().endswith('.pdf'):
            return Response({'error': 'Only PDF files are supported for uploading'}, status=400)

        # Save file to a temporary path
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs')
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.name)

        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        try:
            # Extract text from PDF
            reader = PdfReader(file_path)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'

            if not text.strip():
                return Response({'error': 'No text found in the PDF'}, status=400)

            # Split text into chunks
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            chunks = splitter.split_text(text)

            # Create embeddings using HuggingFace
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

            # Create FAISS vector store from text chunks
            vectorstore = FAISS.from_texts(chunks, embeddings)

            # Define the user-specific vectorstore path
            user_vectorstore_dir = "vectorstores"  # Corrected directory name
            os.makedirs(user_vectorstore_dir, exist_ok=True)
            user_vectorstore_path = os.path.join(
                user_vectorstore_dir, f"{request.user.username}_vectorstore")

            # Save the vectorstore locally
            vectorstore.save_local(user_vectorstore_path)

            return Response(
                {'message': 'PDF processed and vector store created successfully',
                 'filename': file.name,
                 'chunks': len(chunks),
                 'pages': len(reader.pages)
                 }
            )
        except Exception as e:
            return Response({"error": "Failed to process PDF", "details": str(e)}, status=500)
        finally:
            # Clean up the temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
