from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Tag, ClientTag


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
