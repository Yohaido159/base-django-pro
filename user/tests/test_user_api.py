from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return get_user_model().objects.create(**params)


class PublicUserApiTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_valid_user_success(self):
        payload = {
            "email": "yohaido159@gmail.com",
            "password": "12345",
            "name": "yohai"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload.get("password")))
        self.assertNotIn("password", res.data)

    def test_user_exsist(self):
        payload = {
            "email": "test@example.com",
            "password": "123"
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_to_short(self):
        payload = {
            "email": "test@example.com",
            "password": "123"
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exsist = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()

        self.assertFalse(user_exsist)
