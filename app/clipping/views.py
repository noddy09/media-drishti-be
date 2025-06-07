from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Clip
from .serializers import ClipSerializer

# Create your views here.

class ClipViewSet(viewsets.ModelViewSet):
    queryset = Clip.objects.all()
    serializer_class = ClipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
