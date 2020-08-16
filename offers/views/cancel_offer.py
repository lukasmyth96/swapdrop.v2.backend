from rest_framework.response import Response
from rest_framework import serializers
from django.http import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound

from products.models import Product
from offers.views._base_offer_endpoint import BaseOfferEndpoint, OfferDoesNotExist


class CancelOffer(BaseOfferEndpoint):
    
    def post(self, request):
        try:
            desired_product_id, offered_product_id = self.parse_payload(
                request)
            desired_product, offered_product = self.get_products(desired_product_id,
                                                                 offered_product_id)
            self.validate_permissions(desired_product, offered_product)
            self.assert_offer_exists(desired_product, offered_product)
            self.cancel_offer_in_db(desired_product, offered_product)
            response = Response('Offer canceled', 200)
        except serializers.ValidationError as exc:
            response = HttpResponseBadRequest(
                f'Invalid submission payload format: \n {exc}')
        except Product.DoesNotExist:
            response = HttpResponseBadRequest(
                'Not product exists with given ID')
        except PermissionError as exc:
            response = HttpResponseForbidden(exc)
        except OfferDoesNotExist:
            response = HttpResponseNotFound('Offer does not exist')
        return response

    def validate_permissions(self, desired_product, offered_product):
        errors = []

        if desired_product.is_owned_by(self.request.user):
            errors.append('The user owns the desired product')

        if not offered_product.is_owned_by(self.request.user):
            errors.append('User does not own the offered product')

        if errors:
            raise PermissionError(', '.join(errors))

    def cancel_offer_in_db(self, desired_product, offered_product):
        desired_product.pending_offers.remove(offered_product)
