from django.test import TestCase

from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        email = "yohaido159@gmail.com"
        password = "Test12345"
        user = get_user_model().objects.create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_normalize(self):
        email = "test@GMAIL.COM"
        user = get_user_model().objects.create_user(email, "test123")

        self.assertEqual(user.email, email.lower())

    def test_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "213")

    def test_superuser_create(self):
        user = get_user_model().objects.create_superuser("yohai@gmail.com", "123")

        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
