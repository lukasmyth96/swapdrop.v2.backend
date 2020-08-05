import json
from uuid import uuid4
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Product
from products.model_enums import ProductStatus


class MakeCancelTestCase(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='user1_password')
        self.product1 = Product.objects.create(owner=self.user1, title='product1')

        self.user2 = User.objects.create_user(username='user2')
        self.product2 = Product.objects.create(owner=self.user2, title='product2')

        self.client = APIClient()
        self.client.login(username='user1', password='user1_password')
        refresh = RefreshToken.for_user(self.user1)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(refresh.access_token))

        # add product1 to pending_offers of product2
        self.product2.pending_offers.add(self.product1)
        self.assertTrue(self.product1 in self.product2.pending_offers.all())

    def send_request_and_refresh_objects(self, payload):
        response = self.client.post('/offers/cancel/', payload, format='json')
        self.product1.refresh_from_db()  # important!
        self.product2.refresh_from_db()
        return response

    def test_successfull_call(self):
        payload = {'desiredProductId': self.product2.id,
                   'offeredProductId': self.product1.id}
        response = self.send_request_and_refresh_objects(payload)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.product1 in self.product2.pending_offers.all())

    def test_fail_if_invalid_payload_field(self):
        payload = {'invalid_field': self.product2.id,
                   'offeredProductIds': self.product1.id}
        response = self.send_request_and_refresh_objects(payload)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(self.product1 in self.product2.pending_offers.all())

    def test_fail_if_product_id_that_does_not_exist(self):
        payload = {'desiredProductId': str(uuid4()),
                  'offeredProductIds': self.product1.id}
        response = self.send_request_and_refresh_objects(payload)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(self.product1 in self.product2.pending_offers.all())

    def test_fail_if_desired_product_owned_by_current_user(self):
        payload = {'desiredProductId': self.product1.id,
                   'offeredProductId': self.product2.id}  # note order of products reverse here
        response = self.send_request_and_refresh_objects(payload)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.product1 in self.product2.pending_offers.all())

    def test_fail_if_offered_product_not_owned_by_current_user(self):
        payload = {'desiredProductId': self.product2.id,
                    'offeredProductId': self.product2.id}  
        response = self.send_request_and_refresh_objects(payload)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.product1 in self.product2.pending_offers.all())

    def test_fail_if_offer_does_not_exist(self):
        self.product2.pending_offers.remove(self.product1)  # remove offer for this test
        payload = {'desiredProductId': self.product2.id,
                   'offeredProductId': self.product1.id}
        response = self.send_request_and_refresh_objects(payload)
        self.assertEqual(response.status_code, 404)