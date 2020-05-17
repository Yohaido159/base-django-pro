from unittest.mock import patch

from django.test import TestCase

from django.contrib.auth import get_user_model

from core import models


def sample_user(email="test@example.com", password="12345"):
    return get_user_model().objects.create_user(email=email, password=password)


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

    def test_tag_str(self):
        tag = models.Tag.objects.create(
            user=sample_user(), name="Vegen"
        )

        self.assertEqual(str(tag), tag.name)

    def test_recipe_str(self):
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title="stack and mushroom sauce",
            time_minutes=5,
            price=5.00,
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch("uuid.uuid4")
    def test_test_filename_uuid(self, mock_uuid):
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, "myimage.jpg")

        exp_path = f"upload/recipe/{uuid}.jpg"

        self.assertEqual(file_path, exp_path)
