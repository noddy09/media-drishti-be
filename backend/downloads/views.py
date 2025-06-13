from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Download
from .serializers import DownloadSerializer

# Create your views here.

class DownloadViewSet(viewsets.ModelViewSet):
    queryset = Download.objects.all()
    serializer_class = DownloadSerializer
    permission_classes = [permissions.IsAuthenticated]
