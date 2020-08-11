from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest

from products.serializers import ProductSerializer
from products.models import Product
from products.model_enums import ProductStatus


class ProductNotLive(Exception):
    pass


class ReviewOffersView(APIView):

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            self.assert_product_is_live(product=product)
            self.validate_permissions(product=product)

            offered_products = product.pending_offers.all().filter(status=ProductStatus.LIVE)
            serialized_offers = [ProductSerializer(instance=offered_product).data for offered_product in offered_products]
            response = Response(data=serialized_offers, status=HTTP_200_OK)
        except ValidationError as exc:
            response = HttpResponseBadRequest(str(exc.error_list[0]))
        except (PermissionError, ProductNotLive):
            response = HttpResponseForbidden("You do not have permission to view offers on this product")
        except Product.DoesNotExist:
            response = HttpResponseNotFound("Product does not exist")
        return response

    @staticmethod
    def assert_product_is_live(product: Product):
        if not product.is_live:
            raise ProductNotLive()

    def validate_permissions(self, product: Product):
        if not product.is_owned_by(self.request.user):
            raise PermissionError()
