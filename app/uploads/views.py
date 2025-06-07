from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Upload
from .serializers import UploadSerializer

# Create your views here.

class UploadViewSet(viewsets.ModelViewSet):
    queryset = Upload.objects.all()
    serializer_class = UploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
