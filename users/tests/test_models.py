from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from ..choices_types import ProfileRoles

User = get_user_model()


class TestUserModel(APITestCase):
    def test_create_superuser_create_profile_role(self):
        user = User.objects.create_superuser(email='super@super.super', password='strong')
        self.assertTrue(user.password)
        self.assertTrue(user.is_active)
        self.assertTrue(user.last_login)
        self.assertTrue(user.date_joined)
        self.assertEqual(user.email, 'super@super.super')
        self.assertEqual(user.role, ProfileRoles.SUPERUSER)

    def test_create_user_create_profile_role(self):
        user = User.objects.create_user(email='user@user.user')
        self.assertFalse(user.is_active)
        self.assertTrue(user.last_login)
        self.assertTrue(user.date_joined)
        self.assertEqual(user.email, 'user@user.user')
        self.assertEqual(user.role, ProfileRoles.LEARNER)
