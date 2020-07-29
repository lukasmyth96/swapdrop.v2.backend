from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, generics

from products.serializers import ProductSerializer
from products.models import Product
from products.model_enums import ProductStatus


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class FeedListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    model = serializer_class.Meta.model
    
    def get_queryset(self):
        products = Product.objects.filter(status=ProductStatus.LIVE).exclude(owner=self.request.user)
        return products

