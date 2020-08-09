from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from django.http import HttpResponseForbidden

from products.serializers import ProductSerializer
from products.models import Product
from products.model_enums import ProductStatus


class ProductNotLive(Exception):
    pass


class ReviewOffersView(APIView):

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            offered_products = product.pending_offers.all().filter(status=ProductStatus.LIVE)
            serialized_offers = [ProductSerializer(instance=offered_product).data for offered_product in offered_products]
            response = Response(data=serialized_offers, status=HTTP_200_OK)
        except (PermissionError, ProductNotLive):
            response = HttpResponseForbidden("You do not have permission to view the offers")
        return response

    @staticmethod
    def assert_product_is_live(product: Product):
        if not product.is_live:
            raise ProductNotLive()

    def validate_permissions(self, product: Product):
        if not product.is_owned_by(self.request.user):
            raise PermissionError()
