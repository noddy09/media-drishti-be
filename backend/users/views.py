from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import permissions, viewsets

from .serializers import UserSerializer
from backend.auditlog.models import AuditLog
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        user = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='other',
            description=f"Created user {user.username}",
            tenant='default',
        )

    def perform_update(self, serializer):
        user = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='other',
            description=f"Updated user {user.username}",
            tenant='default',
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            user=self.request.user,
            action='other',
            description=f"Deleted user {instance.username}",
            tenant='default',
        )
        instance.delete()
