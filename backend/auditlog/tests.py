from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import AuditLog


class AuditLogDeletePermissionTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        self.employee = User.objects.create_user('employee', 'e@e.com', 'pass', is_staff=True)
        self.log = AuditLog.objects.create(user=self.admin, action='clip', description='x', tenant='default')

    def test_non_admin_cannot_delete(self):
        self.client.force_authenticate(self.employee)
        resp = self.client.delete(f'/api/auditlog/auditlog/{self.log.id}/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.delete(f'/api/auditlog/auditlog/{self.log.id}/')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
