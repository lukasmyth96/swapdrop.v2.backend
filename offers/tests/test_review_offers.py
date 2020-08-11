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
        self.user1 = User.objects.create_user(username='user1', password='user1_password')
        self.product1 = Product.objects.create(owner=self.user1, title='product1')
            
        self.user2 = User.objects.create_user(username='user2', password='user2_password')
        self.product2 = Product.objects.create(owner=self.user2, title='product2')

        self.client = APIClient()
        self.client.login(username='user1', password='user1_password')
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))
        self.product1.pending_offers.add(self.product2)

    def test_successfull_call(self):

        response = self.client.get(f'/offers/review/{self.product1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [ProductSerializer(self.product2).data])
