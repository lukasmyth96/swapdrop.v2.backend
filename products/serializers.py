from rest_framework import serializers

from products.models import Product


class ProductSerializer(serializers.ModelSerializer):

    class Meta:

        model = Product
        exclude = ['pending_offers', 'rejected_offers', 'agreed_swap']
        read_only_fields = ["owner"]

    def create(self, validated_data):
        instance = self.Meta.model(**validated_data)
        instance.owner = self.context["request"].user
        instance.save()
        return instance
