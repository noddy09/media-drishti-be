from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Tag, ClipTag
from .serializers import TagSerializer, ClipTagSerializer
from backend.auditlog.models import AuditLog

# Create your views here.

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        tag = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='tag',
            description=f"Created tag '{tag.name}'",
            tenant='default',
        )

    def perform_update(self, serializer):
        tag = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='tag',
            description=f"Updated tag '{tag.name}'",
            tenant='default',
        )

    def perform_destroy(self, instance):
        if self.request.user.role != 'admin':
            raise PermissionDenied("Only admins can delete tags.")
        AuditLog.objects.create(
            user=self.request.user,
            action='tag',
            description=f"Deleted tag '{instance.name}'",
            tenant='default',
        )
        instance.delete()

class ClipTagViewSet(viewsets.ModelViewSet):
    queryset = ClipTag.objects.all()
    serializer_class = ClipTagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        clipt = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='tag',
            description=f"Assigned tag '{clipt.tag}' to clip {clipt.clip_id}",
            tenant='default',
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            user=self.request.user,
            action='tag',
            description=f"Removed tag '{instance.tag}' from clip {instance.clip_id}",
            tenant='default',
        )
        instance.delete()
