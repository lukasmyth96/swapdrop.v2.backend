import json
from uuid import uuid4
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Product
from products.model_enums import ProductStatus


class MakeRejectTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', password='user1_password')
        self.product1 = Product.objects.create(
            owner=self.user1, title='product1')

        self.user2 = User.objects.create_user(username='user2')
        self.product2 = Product.objects.create(
            owner=self.user2, title='product2')

        self.client = APIClient()
        self.client.login(username='user1', password='user1_password')
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))

        # remove product1 from pending_offers of product2 and adding it to the rejected_offers and then checking if it was done
        self.product2.pending_offers.remove(self.product1)
        self.product2.rejected_offers.add(self.product1)
        self.assertFalse(self.product1 in self.product2.pending_offers.all())
        self.assertTrue(self.product1 in self.product2.rejected_offers.all())

    def test_successfull_call(self):
        payload = {'desiredProductId': self.product2.id,
                   'offeredProductId': self.product1.id}
        response = self.client.post('/offers/reject/', payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.product1 in self.product2.pending_offers.all())
        # check if it moved into rejected_offers
        self.assertTrue(self.product1 in self.product2.rejected_offers.all())

    def test_fail_if_invalid_payload_field(self):
        payload = {'invalid_field': self.product2.id,
                   'offeredProductIds': self.product1.id}
        response = self.client.post('/offers/reject/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(self.product1 in self.product2.pending_offers.all())
        self.assertFalse(self.product1 in self.product2.rejected_offers.all())

    def test_fail_if_product_id_that_does_not_exist(self):
        payload = {'desiredProductId': str(uuid4()),
                   'offeredProductIds': self.product1.id}
        response = self.client.post('/offers/make/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(self.product1 in self.product2.pending_offers.all())
        self.assertFalse(self.product1 in self.product2.rejected_offers.all())

    def test_fail_if_desired_product_not_owned_by_current_user(self):
        payload = {'desiredProductId': self.product2.id,
                   'offeredProductId': self.product1.id}  # note order of products reverse here
        response = self.client.post('/offers/reject/', payload, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.product1 in self.product2.pending_offers.all())
        self.assertFalse(self.product1 in self.product2.rejected_offers.all())

    def test_fail_if_offer_does_not_exist(self):
        self.product2.pending_offers.remove(
            self.product1)  # remove offer for this test
        payload = {'desiredProductId': self.product2.id,
                   'offeredProductId': self.product1.id}
        response = self.client.post('/offers/reject/', payload, format='json')
        self.assertEqual(response.status_code, 404)
