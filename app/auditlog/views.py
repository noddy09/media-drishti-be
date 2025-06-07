from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import AuditLog
from .serializers import AuditLogSerializer

# Create your views here.

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
