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
        # Save with user and user-provided name if present
        name = self.request.data.get('name')
        serializer.save(uploaded_by=self.request.user, name=name)

