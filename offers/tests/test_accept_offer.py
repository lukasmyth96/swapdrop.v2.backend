import json
from uuid import uuid4
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from products.models import Product
from products.model_enums import ProductStatus


class MakeAcceptTestCase(APITestCase):

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

        # does the same thing that accept_offer_in_db in accept.offer does and checks if it was done succesfully
        self.product2.pending_offers.remove(self.product1)
        self.product1.agreed_swap = self.product2
        self.product2.agreed_swap = self.product1
        self.product1.status = ProductStatus.PENDING_CHECKOUT
        self.product2.status = ProductStatus.PENDING_CHECKOUT
        # I am a little unsure but I think that it needs to save the changes before checking anything
        self.product1.save()
        self.product2.save()

        self.assertFalse(self.product1 in self.product2.pending_offers.all())
        self.assertTrue(self.product1.agreed_swap == self.product2)
        self.assertTrue(self.product2.agreed_swap == self.product1)
        self.assertTrue(self.product1.status == ProductStatus.PENDING_CHECKOUT)
        self.assertTrue(self.product2.status == ProductStatus.PENDING_CHECKOUT)

    def test_successfull_call(self):
        payload = {'desiredProductId': self.product2.id,
                   'offeredProductId': self.product1.id}
        response = self.client.post('/offers/accept/', payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.product1 in self.product2.pending_offers.all())
        self.assertTrue(self.product1 in self.product2.pending_offers.all())
        self.assertFalse(self.product1.agreed_swap == self.product2)
        self.assertFalse(self.product2.agreed_swap == self.product1)
        self.assertFalse(self.product1.status ==
                         ProductStatus.PENDING_CHECKOUT)
        self.assertFalse(self.product2.status ==
                         ProductStatus.PENDING_CHECKOUT)

    def test_fail_if_invalid_payload_field(self):
        payload = {'invalid_field': self.product2.id,
                   'offeredProductIds': self.product1.id}
        response = self.client.post('/offers/accept/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(self.product1 in self.product2.pending_offers.all())
        self.assertTrue(self.product1 in self.product2.pending_offers.all())
        self.assertFalse(self.product1.agreed_swap == self.product2)
        self.assertFalse(self.product2.agreed_swap == self.product1)
        self.assertFalse(self.product1.status ==
                         ProductStatus.PENDING_CHECKOUT)
        self.assertFalse(self.product2.status ==
                         ProductStatus.PENDING_CHECKOUT)

    def test_fail_if_product_id_that_does_not_exist(self):
        payload = {'desiredProductId': str(uuid4()),
                   'offeredProductIds': self.product1.id}
        response = self.client.post('/offers/make/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(self.product1 in self.product2.pending_offers.all())
        self.assertTrue(self.product1 in self.product2.pending_offers.all())
        self.assertFalse(self.product1.agreed_swap == self.product2)
        self.assertFalse(self.product2.agreed_swap == self.product1)
        self.assertFalse(self.product1.status ==
                         ProductStatus.PENDING_CHECKOUT)
        self.assertFalse(self.product2.status ==
                         ProductStatus.PENDING_CHECKOUT)

    def test_fail_if_desired_product_owned_by_current_user(self):
        payload = {'desiredProductId': self.product1.id,
                   'offeredProductId': self.product2.id}  # note order of products reverse here
        response = self.client.post('/offers/accept/', payload, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.product1 in self.product2.pending_offers.all())
        self.assertTrue(self.product1 in self.product2.pending_offers.all())
        self.assertFalse(self.product1.agreed_swap == self.product2)
        self.assertFalse(self.product2.agreed_swap == self.product1)
        self.assertFalse(self.product1.status ==
                         ProductStatus.PENDING_CHECKOUT)
        self.assertFalse(self.product2.status ==
                         ProductStatus.PENDING_CHECKOUT)

    def test_fail_if_offer_does_not_exist(self):
        self.product2.pending_offers.remove(
            self.product1)  # remove offer for this test
        payload = {'desiredProductId': self.product2.id,
                   'offeredProductId': self.product1.id}
        response = self.client.post('/offers/accept/', payload, format='json')
        self.assertEqual(response.status_code, 404)

    def test_fail_if_desired_or_offered_product_not_LIVE(self):
        payload = {'desiredProductId': self.product2.id,
                   'offeredProductId': self.product1.id}
        response = self.client.post('/offers/accept/', payload, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.product1.status == ProductStatus.LIVE)
        self.assertFalse(self.product2.status == ProductStatus.LIVE)
