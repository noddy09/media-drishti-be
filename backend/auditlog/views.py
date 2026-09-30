from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import AuditLog
from .serializers import AuditLogSerializer
from backend.users.roles import is_staff_or_admin

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if not is_staff_or_admin(self.request.user):
            raise PermissionDenied("Only admins can delete audit logs.")
        instance.delete()