import uuid

from django.db import models
from django.contrib.auth.models import User
from django_enumfield import enum

from mysite.settings import IMAGE_UPLOAD_DIMENSIONS, IMAGE_UPLOAD_QUALITY
from products.model_enums import ProductStatus
from products.utils import resize_rotate_rename_compress_image


class Product(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = enum.EnumField(ProductStatus, default=ProductStatus.LIVE)
    image1 = models.ImageField(blank=True, upload_to="product_images")

    def __str__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.image1 = resize_rotate_rename_compress_image(image=self.image1, dims=IMAGE_UPLOAD_DIMENSIONS, quality=IMAGE_UPLOAD_QUALITY, filename=self.title)
        super(Product, self).save(force_insert=False, force_update=False, using=None, update_fields=None)
