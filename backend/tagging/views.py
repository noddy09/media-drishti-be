import csv
import io

from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import Tag, ClipTag, ClientTag
from .serializers import TagSerializer, ClipTagSerializer, ClientTagSerializer
from backend.auditlog.models import AuditLog
from backend.clipping.models import Clip
from backend.users.roles import is_staff_or_admin

# Create your views here.

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Clients only see tags mapped to them; staff/superusers see all
        user = self.request.user
        if is_staff_or_admin(user):
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

    @action(detail=False, methods=['post'])
    def bulk_assign(self, request):
        if not is_staff_or_admin(request.user):
            raise PermissionDenied("Only staff/admins can bulk-assign tags.")

        clip_ids = request.data.get('clip_ids') or []
        tag_ids = request.data.get('tag_ids') or []

        valid_clip_ids = set(Clip.objects.filter(id__in=clip_ids).values_list('id', flat=True))
        valid_tag_ids = set(Tag.objects.filter(id__in=tag_ids).values_list('id', flat=True))

        created_count = 0
        for clip_id in valid_clip_ids:
            for tag_id in valid_tag_ids:
                _, created = ClipTag.objects.get_or_create(clip_id=clip_id, tag_id=tag_id)
                if created:
                    created_count += 1

        AuditLog.objects.create(
            user=request.user,
            action='tag',
            description=f"Bulk-assigned {len(tag_ids)} tag(s) to {len(clip_ids)} clip(s)",
            tenant='default',
        )

        return Response({'created_count': created_count})

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

    @action(detail=False, methods=['post'])
    def bulk_import(self, request):
        upload_file = request.FILES.get('file')
        if upload_file is None:
            return Response({'created_count': 0, 'errors': [{'row': 0, 'reason': "No 'file' provided"}]})

        User = get_user_model()
        reader = csv.DictReader(io.TextIOWrapper(upload_file.file, encoding='utf-8'))

        created_count = 0
        errors = []
        for row_num, row in enumerate(reader, start=2):
            username = (row.get('client_username') or '').strip()
            tag_name = (row.get('tag_name') or '').strip()

            user = User.objects.filter(username=username).first()
            if user is None:
                errors.append({'row': row_num, 'reason': f"user '{username}' not found"})
                continue

            tag = Tag.objects.filter(name=tag_name).first()
            if tag is None:
                errors.append({'row': row_num, 'reason': f"tag '{tag_name}' not found"})
                continue

            _, created = ClientTag.objects.get_or_create(client=user, tag=tag)
            if created:
                created_count += 1

        AuditLog.objects.create(
            user=request.user,
            action='other',
            description=f"Bulk-imported {created_count} client-tag mapping(s) from CSV",
            tenant='default',
        )

        return Response({'created_count': created_count, 'errors': errors})
