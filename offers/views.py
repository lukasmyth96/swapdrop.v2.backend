from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden

from products.models import Product
from products.model_enums import ProductStatus


class MakeOffer(APIView):

    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        response = Response('Offers created', 200)
        desired_product, offered_products, errors = self.get_cleaned_data(request)

        if errors:
            response = HttpResponseForbidden(', '.join(errors))
        else:
            for offered_product in offered_products:
                desired_product.pending_offers.add(offered_product)

        return response

    def get_cleaned_data(self, request):

        desired_product, dp_errors = self.get_cleaned_desired_product(request)
        offered_products, op_errors = self.get_cleaned_offered_product(request)
        errors = dp_errors + op_errors
        
        return desired_product, offered_products, errors

    def get_cleaned_desired_product(self, request):
        errors = []

        desired_product_id = request.data['desiredProductId']
        desired_product = Product.objects.get(id=desired_product_id)
        if not is_live(desired_product):
            errors.append('Desired Product is not LIVE')

        if user_owns_product(request.user, desired_product):
            errors.append('The user already owns the desired product')

        return desired_product, errors
    
    def get_cleaned_offered_product(self, request):
        errors = []

        offered_product_ids = request.data['offeredProductIds']
        offered_products = Product.objects.filter(id__in=offered_product_ids)
        if not all([is_live(product) for product in offered_products]):
            errors.append('Not all offered products are live')

        if not all([user_owns_product(request.user, product) for product in offered_products]):
            errors.append('User does not own all offered products')

        return offered_products, errors



def is_live(product):
    return product.status == ProductStatus.LIVE


def user_owns_product(user, product):
    return product.owner == user


