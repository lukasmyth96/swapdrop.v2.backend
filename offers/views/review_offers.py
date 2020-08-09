from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from django.http import HttpResponseForbidden

from products.serializers import ProductSerializer
from products.models import Product
from products.model_enums import ProductStatus


class ReviewOffersView(APIView):

    def get(self, request, product_id):
        product = Product.objects.get(id=product_id)
        if product.is_owned_by(self.request.user):   
            offered_products = product.pending_offers.all().filter(status=ProductStatus.LIVE)
            serialized_offers = [ProductSerializer(instance=offered_product).data for offered_product in offered_products]
            response = Response(data=serialized_offers, status=HTTP_200_OK)
        else:
            response = HttpResponseForbidden("You do not have permission to view the offers")
        return response
