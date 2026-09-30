import fitz
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status

from backend.uploads.models import Upload
from backend.clipping.models import Clip
from .models import Download


class DownloadRetrieveLoggingTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')

        doc = fitz.open()
        doc.new_page(width=100, height=100)
        pdf_bytes = doc.tobytes()
        doc.close()

        self.upload = Upload.objects.create(
            file=SimpleUploadedFile('test.pdf', pdf_bytes, content_type='application/pdf'),
            file_type='pdf',
            uploaded_by=self.admin,
        )
        Clip.objects.create(
            upload=self.upload, x=0, y=0, width=50, height=50, page_number=1, created_by=self.admin,
        )
        self.download = Download.objects.create(upload=self.upload, downloaded_by='seed', tenant='default')

    def test_retrieve_logs_download_record(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get(f'/api/downloads/downloads/{self.download.id}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        records = Download.objects.filter(upload=self.upload, downloaded_by='admin')
        self.assertEqual(records.count(), 1)


class DownloadListScopingTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        self.client_a = User.objects.create_user('client_a', 'ca@a.com', 'pass')
        self.client_b = User.objects.create_user('client_b', 'cb@a.com', 'pass')

        doc = fitz.open()
        doc.new_page(width=100, height=100)
        pdf_bytes = doc.tobytes()
        doc.close()

        self.upload = Upload.objects.create(
            file=SimpleUploadedFile('test.pdf', pdf_bytes, content_type='application/pdf'),
            file_type='pdf',
            uploaded_by=self.admin,
        )

        self.download_a = Download.objects.create(upload=self.upload, downloaded_by='client_a', tenant='default')
        self.download_b = Download.objects.create(upload=self.upload, downloaded_by='client_b', tenant='default')

    def test_client_only_sees_own_downloads(self):
        self.client.force_authenticate(self.client_a)
        resp = self.client.get('/api/downloads/downloads/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        results = resp.data['results']
        ids = {item['id'] for item in results}
        self.assertEqual(ids, {self.download_a.id})

    def test_admin_sees_all_downloads(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/downloads/downloads/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        results = resp.data['results']
        ids = {item['id'] for item in results}
        self.assertEqual(ids, {self.download_a.id, self.download_b.id})
