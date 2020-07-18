import uuid
from django.db import models
from django.contrib.auth.models import User
from django_enumfield import enum

from products.model_enums import ProductStatus


class Product(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = enum.EnumField(ProductStatus, default=ProductStatus.LIVE)

    def __str__(self):
        return self.title
