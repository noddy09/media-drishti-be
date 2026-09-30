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
