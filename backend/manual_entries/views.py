from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import ManualEntry
from .serializers import ManualEntrySerializer
from backend.auditlog.models import AuditLog

# Create your views here.

class ManualEntryViewSet(viewsets.ModelViewSet):
    queryset = ManualEntry.objects.all()
    serializer_class = ManualEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        entry = serializer.save(created_by=self.request.user)
        AuditLog.objects.create(
            user=self.request.user,
            action='manual_entry',
            description=f"Created manual entry '{entry.title}'",
            tenant='default',
        )

    def perform_update(self, serializer):
        entry = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action='manual_entry',
            description=f"Updated manual entry '{entry.title}'",
            tenant='default',
        )

    def perform_destroy(self, instance):
        AuditLog.objects.create(
            user=self.request.user,
            action='manual_entry',
            description=f"Deleted manual entry '{instance.title}'",
            tenant='default',
        )
        instance.delete()
