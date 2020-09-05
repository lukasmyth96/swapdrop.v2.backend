from rest_framework.response import Response
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound
from rest_framework import serializers

from products.models import Product
from products.model_enums import ProductStatus
from offers.views._base_offer_endpoint import BaseOfferEndpoint, OfferDoesNotExist


class ProductNotLive(Exception):
    pass


class AcceptOffer(BaseOfferEndpoint):

    def post(self, request):
        try:
            desired_product_id, offered_product_id = self.parse_payload(
                request)
            desired_product, offered_product = self.get_products(desired_product_id,
                                                                 offered_product_id)
            self.validate_permissions(desired_product)
            self.assert_products_are_live(desired_product, offered_product)
            self.assert_offer_exists(desired_product, offered_product)
            self.accept_offer_in_db(desired_product, offered_product)
            response = Response('Offer accepted', 200)
        except serializers.ValidationError as exc:
            response = HttpResponseBadRequest(
                f'Invalid submission payload format: \n {exc}')
        except Product.DoesNotExist:
            response = HttpResponseBadRequest(
                'Not product exists with given ID')
        except PermissionError as exc:
            response = HttpResponseForbidden(exc)
        except ProductNotLive:
            response = HttpResponseBadRequest(
                'Desired or offered product is not LIVE')
        except OfferDoesNotExist:
            response = HttpResponseNotFound('Offer does not exist')

        return response

    def validate_permissions(self, desired_product):
        errors = []

        if not desired_product.is_owned_by(self.request.user):
            errors.append('The user does not own the desired product')

        if errors:
            raise PermissionError(', '.join(errors))
    
    @staticmethod
    def assert_products_are_live(desired_product, offered_product):

        if not (offered_product.is_live and desired_product.is_live):
            raise ProductNotLive()

    @staticmethod
    def accept_offer_in_db(desired_product, offered_product):

        desired_product.pending_offers.remove(offered_product)

        offered_product.agreed_swap = desired_product
        desired_product.agreed_swap = offered_product

        offered_product.status = ProductStatus.PENDING_CHECKOUT
        desired_product.status = ProductStatus.PENDING_CHECKOUT

        offered_product.save()
        desired_product.save()
