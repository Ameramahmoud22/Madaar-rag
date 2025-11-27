from django.urls import path
from .views import LoginView, UploadPDFView

urlpatterns = [

    path('login/', LoginView.as_view(), name='login'),
    path('upload-pdf/', UploadPDFView.as_view(), name='upload-pdf'),

]
