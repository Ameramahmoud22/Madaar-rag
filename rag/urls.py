from django.urls import path
from .views import LoginView, UploadPDFView

urlpatterns = [

    path('login/', LoginView.as_view()),
    path('upload-pdf/', UploadPDFView.as_view()),

]
