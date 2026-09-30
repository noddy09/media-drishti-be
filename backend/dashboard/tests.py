from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

from backend.uploads.models import Upload
from backend.clipping.models import Clip
from backend.auditlog.models import AuditLog


class DashboardStatsTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        upload = Upload.objects.create(
            file='test.pdf', file_type='pdf', uploaded_by=self.admin, name='test'
        )
        Clip.objects.create(
            upload=upload, x=0, y=0, width=10, height=10, created_by=self.admin
        )

    def test_admin_sees_nonzero_counts(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/dashboard/dashboard-stats/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreater(resp.data['total_uploads'], 0)
        self.assertGreater(resp.data['total_clips'], 0)


class RecentActivityTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        AuditLog.objects.create(user=self.admin, action='login', description='first', tenant='t1')
        AuditLog.objects.create(user=self.admin, action='upload', description='second', tenant='t1')

    def test_recent_activity_newest_first(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/dashboard/recent-activity/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        descriptions = [row['description'] for row in resp.data]
        self.assertEqual(descriptions, ['second', 'first'])
