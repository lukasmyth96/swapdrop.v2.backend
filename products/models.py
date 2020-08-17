import uuid

from django.db import models
from django.contrib.auth.models import User
from django_enumfield import enum

from mysite.settings import IMAGE_UPLOAD_DIMENSIONS, IMAGE_UPLOAD_QUALITY
from products.model_enums import ProductStatus
from products.utils import resize_rotate_rename_compress_image


class Product(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = enum.EnumField(ProductStatus, default=ProductStatus.LIVE)

    pending_offers = models.ManyToManyField(
        'Product', blank=True, related_name='products_pending_offers')
    rejected_offers = models.ManyToManyField(
        'Product', blank=True, related_name='products_rejected_offers')
    agreed_swap = models.ForeignKey('Product', null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='products_agreed_swap')

    title = models.CharField(max_length=50)
    image1 = models.ImageField(blank=True, upload_to="product_images")
    is_owned_by_current_user = models.BooleanField(default=(User == owner))

    number_of_offers = models.CharField(max_length=50, default=pending_offers)

    def __str__(self):
        return f'{self.title} OWNED BY {self.owner}'

    @property
    def is_live(self):
        return self.status == ProductStatus.LIVE

    def is_owned_by(self, user):
        return self.owner == user

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.image1 = resize_rotate_rename_compress_image(
            image=self.image1, dims=IMAGE_UPLOAD_DIMENSIONS, quality=IMAGE_UPLOAD_QUALITY, filename=self.title)
        super(Product, self).save(force_insert=False,
                                  force_update=False, using=None, update_fields=None)
