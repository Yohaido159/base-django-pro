from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe
from core import models
from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def sample_user():
    return get_user_model().objects.create_user(email="testyohai@example.com", password="12345")


class PublicTagApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com', password="12345")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_tags(self):
        Tag.objects.create(user=self.user, name="Vegen")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by("-name")
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_limited_to_user(self):
        self.user2 = get_user_model().objects.create_user(
            email='other@example.com', password='12345')
        Tag.objects.create(user=self.user2, name="Fruity")
        tag = Tag.objects.create(user=self.user, name="Comfort Food")

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], tag.name)

    def test_create_new_tag(self):
        payload = {"name": "test tag"}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user, name=payload["name"]).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        payload = {"name": ""}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ing_str(self):
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Cucumber"
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_retrive_tags_of_recipe(self):
        tag1 = Tag.objects.create(user=self.user, name="breakfast")
        tag2 = Tag.objects.create(user=self.user, name="lunch")
        recipe = Recipe.objects.create(
            user=self.user, title="Recipe good", time_minutes=1, price=2.00)
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrive_tags_unique(self):
        tag = Tag.objects.create(user=self.user, name="Breackfast")
        Tag.objects.create(user=self.user, name="lunch")
        recipe1 = Recipe.objects.create(
            user=self.user, title="Recipe test", time_minutes=1, price=2.55)

        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            user=self.user, title="dinner", time_minutes=1, price=22.00)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
