from rest_framework.views import APIView

from products.models import Product
from offers.serializers import BaseOfferSerializer


class OfferDoesNotExist(Exception):
    pass


class BaseOfferEndpoint(APIView):
    @staticmethod
    def parse_payload(request):
        serializer = BaseOfferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        desired_product_id = serializer.validated_data['desired_product_id']
        offered_product_id = serializer.validated_data['offered_product_id']
        return desired_product_id, offered_product_id

    @staticmethod
    def get_products(desired_product_id, offered_product_id):
        desired_product = Product.objects.get(id=desired_product_id)
        offered_product = Product.objects.get(id=offered_product_id)
        return desired_product, offered_product

    @staticmethod
    def assert_offer_exists(desired_product, offered_product):
        if offered_product not in desired_product.pending_offers.all():
            raise OfferDoesNotExist()
