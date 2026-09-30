from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status

from backend.auditlog.models import AuditLog
from backend.uploads.models import Upload
from .models import Clip

# Create your tests here.


class ClipBulkDeleteTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        self.client_user = User.objects.create_user('client', 'c@c.com', 'pass')
        file = SimpleUploadedFile('test.pdf', b'%PDF-1.4', content_type='application/pdf')
        self.upload = Upload.objects.create(file=file, file_type='pdf', uploaded_by=self.admin)

    def _make_clip(self):
        return Clip.objects.create(
            upload=self.upload,
            x=0, y=0, width=10, height=10, page_number=1,
            created_by=self.admin,
        )

    def test_staff_can_bulk_delete(self):
        clip1 = self._make_clip()
        clip2 = self._make_clip()
        self.client.force_authenticate(self.admin)
        audit_count_before = AuditLog.objects.count()

        resp = self.client.post(
            '/api/clipping/clips/bulk_delete/',
            {'clip_ids': [clip1.id, clip2.id]},
            format='json',
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['deleted_count'], 2)
        self.assertEqual(Clip.objects.count(), 0)
        self.assertEqual(AuditLog.objects.count(), audit_count_before + 1)

    def test_client_cannot_bulk_delete(self):
        clip1 = self._make_clip()
        self.client.force_authenticate(self.client_user)

        resp = self.client.post(
            '/api/clipping/clips/bulk_delete/',
            {'clip_ids': [clip1.id]},
            format='json',
        )

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Clip.objects.count(), 1)
