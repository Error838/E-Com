from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    phone = models.CharField(max_length=12)
    address = models.TextField()
    ROLES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=20, choices=ROLES)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)

    class Meta:
        app_label = 'shop'

    # Set custom related_name for groups and user_permissions
    groups = models.ManyToManyField(
        Group,
        blank=True,
        related_name='shop_users'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='shop_users'
    )

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='product_images')

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')

class UserManager(models.Manager):
    def get_admins(self):
        return self.filter(role='admin')

class UserManager(models.Manager):
    def get_customers(self):
        return self.filter(role='customer')

User.add_to_class('objects', UserManager())

