from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='useryohai@example.com',
            password='12345'
        )
        self.client.force_authenticate(self.user)

    def test_retrive_ingredient_list(self):
        Ingredient.objects.create(
            name="Kale",
            user=self.user,
        )
        Ingredient.objects.create(
            name="ingredient1",
            user=self.user,
        )

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limit_to_user(self):
        user2 = get_user_model().objects.create_user(
            "other@example.com",
            "12345"
        )
        Ingredient.objects.create(user=user2, name="Vinger")
        ingredient = Ingredient.objects.create(user=self.user, name="Tumeric")

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)

    def test_create_ingredient_successful(self):
        payload = {"name": "Cabbage"}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user, name=payload["name"]).exists()

        self.assertTrue(exists)

    def test_ingredient_invalid(self):
        payload = {"name": ""}
        res = self.client.post(INGREDIENT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrive_ingredient(self):
        ingredient1 = Ingredient.objects.create(user=self.user, name="ing1")
        ingredient2 = Ingredient.objects.create(user=self.user, name="ing2")
        recipe = Recipe.objects.create(
            user=self.user, title="Recipe 1 ", price=22, time_minutes=3)

        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {"assigned_only": 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrive_unique_ingredient(self):
        ingredient = Ingredient.objects.create(user=self.user, name="ibg1")
        Ingredient.objects.create(user=self.user, name="ibg2")

        recipe1 = Recipe.objects.create(
            user=self.user, title="Recipe1", time_minutes=5, price=22)

        recipe2 = Recipe.objects.create(
            user=self.user, title="Recipe2", time_minutes=5, price=22)

        recipe1.ingredients.add(ingredient)

        res = self.client.get(INGREDIENT_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)
