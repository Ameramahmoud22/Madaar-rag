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
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

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
vectorstore = None


class UploadPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        global vectorstore

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        if not file.name.lower().endswith('.pdf'):
            return Response({'error': 'Only PDF files are supported for uploading'}, status=400)

# save file to media directory
        file_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', file.name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)

# extract text from pdf
        try:
            reader = PdfReader(file_path)
            text = ''
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + '\n'

            if not text.strip():
                return Response({'error': 'There is No text found in the PDF'}, status=400)

        # split text

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            chunk = splitter.split_text(text)

        # create embeddings and store in FAISS
            embeddings = OpenAIEmbeddings()
            global vectorstore
            vectorstore = FAISS.from_texts(chunk, embeddings)

            # vectorstore for each user
            os.makedirs("vectorstore", exist_ok=True)
            user_vectorstore_path = f"vectorstore/{request.user.username}_vectorstore"
            vectorstore.save_local(user_vectorstore_path)

            return Response(
                {'message': 'PDF uploaded successfully ',
                 'filename': file.name,
                 'chunks': len(chunk),
                 'pages': len(reader.pages)
                 }
            )
        except Exception as e:
            return Response({"error": "Failed to process PDF", "details": str(e)}, status=500)
