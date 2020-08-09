from rest_framework import generics
from django.http import HttpResponseForbidden

from products.serializers import ProductSerializer
from products.models import Product
from products.model_enums import ProductStatus


class ReviewOffersView(generics.ListAPIView):
    serializer_class = ProductSerializer
    model = Product

    def get_queryset(self):
        product_id = self.kwargs.get('productId')
        product = Product.objects.get(id=product_id)
        if not product.is_owned_by(self.request.user):
            return HttpResponseForbidden("You do not have permission to view the offers")
        offered_products = product.pending_offers.all().filter(status=ProductStatus.LIVE)
        return offered_products
