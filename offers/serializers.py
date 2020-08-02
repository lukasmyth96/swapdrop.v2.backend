from rest_framework import serializers

class MakeOfferSerializer(serializers.Serializer):
    desiredProductId = serializers.UUIDField(source='desired_product_id')
    offeredProductIds = serializers.ListField(child=serializers.UUIDField(), source='offered_product_ids')

class CancelOfferSerializer(serializers.Serializer):
    desiredProductId = serializers.UUIDField(source='desired_product_id')
    offeredProductId = serializers.UUIDField(source='offered_product_id')
