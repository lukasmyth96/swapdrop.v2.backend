import json
from uuid import uuid4
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Product
from products.model_enums import ProductStatus
from products.serializers import ProductSerializer


class ReviewOffersTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='user1_password')
        self.product1 = Product.objects.create(
            owner=self.user1, title='product1')

        self.user2 = User.objects.create_user(
            username='user2', password='user2_password')
        self.product2 = Product.objects.create(
            owner=self.user2, title='product2')

        self.client = APIClient()
        self.client.login(username='user1', password='user1_password')
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
        self.product1.pending_offers.add(self.product2)

    def test_successfull_call(self):

        response = self.client.get(f'/offers/review/{self.product1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data, [ProductSerializer(self.product2).data])

    def test_fail_if_product_not_owned_by_current_user(self):
        response = self.client.get(f'/offers/review/{self.product2.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(getattr(response, 'data', None))

    def test_fail_if_product_is_not_live(self):
        self.product1.status = ProductStatus.PENDING_CHECKOUT
        self.product1.save()
        response = self.client.get(f'/offers/review/{self.product1.id}/')
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(getattr(response, 'data', None))
        self.assertIsNone(getattr(response, 'data', None))

    def test_fail_if_invalid_product_id_format(self):
        response = self.client.get(f'/offers/review/an_invalid_product_id/')
        self.assertEqual(response.status_code, 400)
        self.assertIsNone(getattr(response, 'data', None))

    def test_fail_if_invalid_product_does_not_exist(self):
        random_uuid = uuid4()
        response = self.client.get(f'/offers/review/{random_uuid}/')
        self.assertEqual(response.status_code, 404)
        self.assertIsNone(getattr(response, 'data', None))
