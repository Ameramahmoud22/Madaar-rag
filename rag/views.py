import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated



class LoginView(APIView):
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
    def post(self, request):
        global vectorstore

        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file uploaded'}, status=400)

        if not file.name.lower().endswith('.pdf'):
            return Response({'error': 'Only PDF files are supported'}, status=400)
