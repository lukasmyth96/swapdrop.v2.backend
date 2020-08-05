from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from django.http import HttpResponseForbidden, HttpResponseBadRequest

from products.models import Product
from offers.serializers import MakeOfferSerializer


class MakeOffer(APIView):

    def post(self, request):

        try:
            desired_product_id, offered_product_ids = self.parse_payload(
                request)
            desired_product, offered_products = self.get_products(desired_product_id,
                                                                  offered_product_ids)
            self.validate_permissions(desired_product, offered_products)
            self.save_offers_in_db(desired_product, offered_products)
            response = Response('Offers created', 200)
        except serializers.ValidationError as exc:
            response = HttpResponseBadRequest(
                f'Invalid submission payload format: \n {exc}')
        except Product.DoesNotExist:
            response = HttpResponseBadRequest(
                'No product exists with given ID')
        except PermissionError as exc:
            response = HttpResponseForbidden(exc)

        return response

    @staticmethod
    def parse_payload(request):
        serializer = MakeOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        desired_product_id = serializer.validated_data['desired_product_id']
        offered_product_ids = serializer.validated_data['offered_product_ids']
        return desired_product_id, offered_product_ids

    @staticmethod
    def get_products(desired_product_id, offered_product_ids):
        desired_product = Product.objects.get(id=desired_product_id)
        offered_products = Product.objects.filter(id__in=offered_product_ids)
        return desired_product, offered_products

    def validate_permissions(self, desired_product, offered_products):
        errors = []

        if not desired_product.is_live:
            errors.append('Desired Product is not LIVE')

        if desired_product.is_owned_by(self.request.user):
            errors.append('The user owns the desired product')

        if not all([product.is_live for product in offered_products]):
            errors.append('Not all offered products are live')

        if not all([product.is_owned_by(self.request.user) for product in offered_products]):
            errors.append('User does not own all offered products')

        if errors:
            raise PermissionError(', '.join(errors))

    @staticmethod
    def save_offers_in_db(desired_product, offered_products):
        for offered_product in offered_products:
            desired_product.pending_offers.add(offered_product)