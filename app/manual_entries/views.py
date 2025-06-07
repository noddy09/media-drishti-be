from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import ManualEntry
from .serializers import ManualEntrySerializer

# Create your views here.

class ManualEntryViewSet(viewsets.ModelViewSet):
    queryset = ManualEntry.objects.all()
    serializer_class = ManualEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
