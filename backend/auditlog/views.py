from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if self.request.user.role != 'admin':
            raise PermissionDenied("Only admins can delete audit logs.")
        instance.delete()