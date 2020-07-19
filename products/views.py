from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets

from products.serializers import ProductSerializer
from products.models import Product


class ProductViewSet(viewsets.ModelViewSet):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

