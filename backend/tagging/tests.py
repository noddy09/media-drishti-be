from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Tag, ClipTag, ClientTag
from backend.uploads.models import Upload
from backend.clipping.models import Clip


class TagVisibilityTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        self.client_user = User.objects.create_user('client1', 'c@c.com', 'pass')
        self.tag_visible = Tag.objects.create(name='visible')
        self.tag_hidden = Tag.objects.create(name='hidden')
        ClientTag.objects.create(client=self.client_user, tag=self.tag_visible)

    def test_client_only_sees_assigned_tags(self):
        self.client.force_authenticate(self.client_user)
        resp = self.client.get('/api/tagging/tags/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [t['name'] for t in resp.data['results']]
        self.assertIn('visible', names)
        self.assertNotIn('hidden', names)

    def test_admin_sees_all_tags(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.get('/api/tagging/tags/')
        names = [t['name'] for t in resp.data['results']]
        self.assertIn('visible', names)
        self.assertIn('hidden', names)


class ClipTagBulkAssignTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        self.client_user = User.objects.create_user('client1', 'c@c.com', 'pass')
        file = SimpleUploadedFile('test.pdf', b'%PDF-1.4', content_type='application/pdf')
        self.upload = Upload.objects.create(file=file, file_type='pdf', uploaded_by=self.admin)
        self.clip1 = Clip.objects.create(
            upload=self.upload, x=0, y=0, width=10, height=10, page_number=1, created_by=self.admin,
        )
        self.clip2 = Clip.objects.create(
            upload=self.upload, x=0, y=0, width=10, height=10, page_number=1, created_by=self.admin,
        )
        self.tag1 = Tag.objects.create(name='tag1')
        self.tag2 = Tag.objects.create(name='tag2')

    def test_staff_can_bulk_assign(self):
        self.client.force_authenticate(self.admin)

        resp = self.client.post(
            '/api/tagging/clip-tags/bulk_assign/',
            {'clip_ids': [self.clip1.id, self.clip2.id], 'tag_ids': [self.tag1.id, self.tag2.id]},
            format='json',
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['created_count'], 4)
        self.assertEqual(ClipTag.objects.count(), 4)

    def test_client_cannot_bulk_assign(self):
        self.client.force_authenticate(self.client_user)

        resp = self.client.post(
            '/api/tagging/clip-tags/bulk_assign/',
            {'clip_ids': [self.clip1.id], 'tag_ids': [self.tag1.id]},
            format='json',
        )

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ClipTag.objects.count(), 0)


class ClientTagBulkImportTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')
        self.client_user = User.objects.create_user('client1', 'c@c.com', 'pass')
        self.tag1 = Tag.objects.create(name='tag1')

    def test_staff_can_bulk_import_csv(self):
        self.client.force_authenticate(self.admin)
        csv_content = (
            "client_username,tag_name\r\n"
            "client1,tag1\r\n"
            "unknownuser,tag1\r\n"
        )
        csv_file = SimpleUploadedFile('clienttags.csv', csv_content.encode('utf-8'), content_type='text/csv')

        resp = self.client.post(
            '/api/tagging/client-tags/bulk_import/',
            {'file': csv_file},
            format='multipart',
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['created_count'], 1)
        self.assertEqual(len(resp.data['errors']), 1)
        self.assertEqual(resp.data['errors'][0]['row'], 3)
        self.assertIn("unknownuser", resp.data['errors'][0]['reason'])
        self.assertEqual(ClientTag.objects.count(), 1)

    def test_client_cannot_bulk_import(self):
        self.client.force_authenticate(self.client_user)
        csv_content = "client_username,tag_name\r\nclient1,tag1\r\n"
        csv_file = SimpleUploadedFile('clienttags.csv', csv_content.encode('utf-8'), content_type='text/csv')

        resp = self.client.post(
            '/api/tagging/client-tags/bulk_import/',
            {'file': csv_file},
            format='multipart',
        )

        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ClientTag.objects.count(), 0)
