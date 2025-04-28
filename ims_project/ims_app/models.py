from django.db import models
from django_mongodb_backend.fields import EmbeddedModelField, ArrayField
from django_mongodb_backend.models import EmbeddedModel

class Supplier(EmbeddedModel):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

class Category(EmbeddedModel):
    name = models.CharField(max_length=100)
    parent_name = models.CharField(max_length=100, blank=True)  # Parent category name (string)
    description = models.TextField(blank=True)

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    instagram_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "customers"
        managed = False

    def __str__(self):
        return self.name

class Product(models.Model):
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    category = EmbeddedModelField(Category, null=True, blank=True)
    tags = ArrayField(models.CharField(max_length=50), null=True, blank=True)
    suppliers = ArrayField(EmbeddedModelField(Supplier), null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
        managed = False

    def __str__(self):
        return self.name
