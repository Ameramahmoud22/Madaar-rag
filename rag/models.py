from django.db import models
from django.contrib.auth.models import User


class PDFDocument(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='pdfs')
    file = models.FileField(upload_to='pdfs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name.split('/')[-1]
