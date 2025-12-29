from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Tag, ClipTag, ClientTag
from .serializers import TagSerializer, ClipTagSerializer, ClientTagSerializer
from backend.auditlog.models import AuditLog

# Create your views here.

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Clients only see tags mapped to them; staff/superusers see all
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return super().get_queryset()
        allowed_tag_ids = ClientTag.objects.filter(client=user).values_list('tag_id', flat=True)
        return Tag.objects.filter(id__in=allowed_tag_ids)

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
        if not self.request.user.is_superuser:
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

class ClientTagViewSet(viewsets.ModelViewSet):
    queryset = ClientTag.objects.all()
    serializer_class = ClientTagSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can manage client-tag mappings

    def perform_create(self, serializer):
        client_tag = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='other',
            description=f"Assigned tag '{client_tag.tag.name}' to client {client_tag.client.username}",
            tenant='default',
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            user=self.request.user,
            action='other',
            description=f"Removed tag '{instance.tag.name}' from client {instance.client.username}",
            tenant='default',
        )
        instance.delete()
