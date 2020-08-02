from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, serializers
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound

from products.models import Product
from products.model_enums import ProductStatus

from offers.serializers import MakeOfferSerializer, CancelOfferSerializer


class OfferDoesNotExist(Exception):
    pass


class MakeOffer(APIView):

    def post(self, request, *args, **kwargs):

        try:
            desired_product_id, offered_product_ids = self.parse_payload(
                request)
            desired_product, offered_products = self.get_products(desired_product_id,
                                                                  offered_product_ids)
            self.validate_permissions(desired_product, offered_products)
            self.save_offers_in_db(desired_product, offered_products)
            response = Response('Offers created', 200)
        except serializers.ValidationError as e:
            response = HttpResponseBadRequest(
                f'Invalid submission payload format: \n {e}')
        except Product.DoesNotExist:
            response = HttpResponseBadRequest(
                'Not product exists with given ID')
        except PermissionError as e:
            response = HttpResponseForbidden(e)

        return response

    def parse_payload(self, request):
        serializer = MakeOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        desired_product_id = serializer.validated_data['desired_product_id']
        offered_product_ids = serializer.validated_data['offered_product_ids']
        return desired_product_id, offered_product_ids

    def get_products(self, desired_product_id, offered_product_ids):
        desired_product = Product.objects.get(id=desired_product_id)
        offered_products = Product.objects.filter(id__in=offered_product_ids)
        return desired_product, offered_products

    def validate_permissions(self, desired_product, offered_products):
        errors = []

        if not is_live(desired_product):
            errors.append('Desired Product is not LIVE')

        if user_owns_product(self.request.user, desired_product):
            errors.append('The user owns the desired product')

        if not all([is_live(product) for product in offered_products]):
            errors.append('Not all offered products are live')

        if not all([user_owns_product(self.request.user, product) for product in offered_products]):
            errors.append('User does not own all offered products')

        if errors:
            raise PermissionError(', '.join(errors))

    def save_offers_in_db(self, desired_product, offered_products):
        for offered_product in offered_products:
            desired_product.pending_offers.add(offered_product)


def is_live(product):
    return product.status == ProductStatus.LIVE


def user_owns_product(user, product):
    return product.owner == user


class CancelOffer(APIView):

    def post(self, request, *args, **kwargs):
        try:
            desired_product_id, offered_product_id = self.parse_payload(
                request)
            desired_product, offered_product = self.get_products(desired_product_id,
                                                                 offered_product_id)
            self.validate_permissions(desired_product, offered_product)
            self.cancel_offer_in_db(desired_product, offered_product)
            response = Response('Offer canceled', 200)
        except serializers.ValidationError as e:
            response = HttpResponseBadRequest(
                f'Invalid submission payload format: \n {e}')
        except Product.DoesNotExist:
            response = HttpResponseBadRequest(
                'Not product exists with given ID')
        except PermissionError as e:
            response = HttpResponseForbidden(e)
        except OfferDoesNotExist:
            response = HttpResponseNotFound('Offer does not exist')
        return response

    def parse_payload(self, request):
        serializer = CancelOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        desired_product_id = serializer.validated_data['desired_product_id']
        offered_product_id = serializer.validated_data['offered_product_id']
        return desired_product_id, offered_product_id

    def get_products(self, desired_product_id, offered_product_id):
        desired_product = Product.objects.get(id=desired_product_id)
        offered_product = Product.objects.get(id=offered_product_id)
        return desired_product, offered_product

    def validate_permissions(self, desired_product, offered_product):
        errors = []

        if user_owns_product(self.request.user, desired_product):
            errors.append('The user owns the desired product')

        if not user_owns_product(self.request.user, offered_product):
            errors.append('User does not own the offered product')

        if errors:
            raise PermissionError(', '.join(errors))

    def cancel_offer_in_db(self, desired_product, offered_product):
        if offered_product in desired_product.pending_offers.all():
            desired_product.pending_offers.remove(offered_product)
        else:
            raise OfferDoesNotExist()
