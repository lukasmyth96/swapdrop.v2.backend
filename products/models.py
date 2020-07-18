import uuid
from django.db import models


class Product(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title
