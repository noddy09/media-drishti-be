from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Clip
from .serializers import ClipSerializer
from backend.auditlog.models import AuditLog

# Create your views here.

class ClipViewSet(viewsets.ModelViewSet):
    queryset = Clip.objects.all()
    serializer_class = ClipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Expect 'upload' as the upload ID in the request
        clip = serializer.save(created_by=self.request.user)
        # No need for separate tag assignment here, handled in serializer
        AuditLog.objects.create(
            user=self.request.user,
            action='clip',
            description=f"Created clip for file '{clip.upload}'",
        )

    def perform_update(self, serializer):
        clip = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='clip',
            description=f"Updated clip for file '{clip.upload}'",
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            user=self.request.user,
            action='clip',
            description=f"Deleted clip for file '{instance.upload}'",
        )
        instance.delete()
