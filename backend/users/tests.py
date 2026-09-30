from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status


class UserUpdateSecurityTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'a@a.com', 'pass')

    def test_patch_password_is_hashed_and_usable(self):
        target = User.objects.create_user('someone', 's@s.com', 'oldpass')
        self.client.force_authenticate(self.admin)
        resp = self.client.patch(f'/api/users/users/{target.id}/', {'password': 'newpass123'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        target.refresh_from_db()
        self.assertNotEqual(target.password, 'newpass123')
        self.assertTrue(target.check_password('newpass123'))

    def test_role_downgrade_clears_superuser_and_staff(self):
        target = User.objects.create_user('promoted', 'p@p.com', 'pass')
        self.client.force_authenticate(self.admin)

        resp = self.client.patch(f'/api/users/users/{target.id}/', {'role': 'admin'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertTrue(target.is_staff)
        self.assertTrue(target.is_superuser)

        resp = self.client.patch(f'/api/users/users/{target.id}/', {'role': 'client'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertFalse(target.is_staff)
        self.assertFalse(target.is_superuser)
