from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions, serializers
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound

from products.models import Product
from products.model_enums import ProductStatus

from offers.serializers import AcceptOfferSerializer


class OfferDoesNotExist(Exception):
    pass

class ProductNotLive(Exception):
    pass


class AcceptOffer(APIView):

    def post(self, request, *args, **kwargs):
        try:
            desired_product_id, offered_product_id = self.parse_payload(
                request)
            desired_product, offered_product = self.get_products(desired_product_id,
                                                                 offered_product_id)
            self.validate_permissions(desired_product, offered_product)
            self.accept_offer_in_db(desired_product, offered_product)
            response = Response('Offer rejected', 200)
        except serializers.ValidationError as e:
            response = HttpResponseBadRequest(
                f'Invalid submission payload format: \n {e}')
        except Product.DoesNotExist:
            response = HttpResponseBadRequest(
                'Not product exists with given ID')
        except PermissionError as e:
            response = HttpResponseForbidden(e)
        except ProductNotLive:
            response = HttpResponseBadRequest('Desired or offered product is not LIVE')
        except OfferDoesNotExist:
            response = HttpResponseNotFound('Offer does not exist')

        return response

    def parse_payload(self, request):
        serializer = AcceptOfferSerializer(data=request.data)
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

        if not desired_product.is_owned_by(self.request.user):
            errors.append('The user does not own the desired product')

        if errors:
            raise PermissionError(', '.join(errors))

    def accept_offer_in_db(self, desired_product, offered_product):
        if not (offered_product.is_live and desired_product.is_live):
            raise ProductNotLive()


        if offered_product in desired_product.pending_offers.all():
            desired_product.pending_offers.remove(offered_product)

            offered_product.agreed_swap = desired_product
            desired_product.agreed_swap = offered_product

            offered_product.status = ProductStatus.PENDING_CHECKOUT
            desired_product.status = ProductStatus.PENDING_CHECKOUT

            offered_product.save()
            desired_product.save()

        else:
            raise OfferDoesNotExist()
