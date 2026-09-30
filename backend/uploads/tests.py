from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status


class UploadPermissionTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        self.employee = User.objects.create_user('employee', 'e@e.com', 'pass', is_staff=True)

    def test_employee_cannot_create_upload(self):
        self.client.force_authenticate(self.employee)
        file = SimpleUploadedFile('test.pdf', b'%PDF-1.4', content_type='application/pdf')
        resp = self.client.post('/api/uploads/', {'file_type': 'pdf', 'file': file})
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_superuser_list_uploads_ok(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/uploads/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
