"""
Django models import statements for UserProfile and Product.
"""
from django.db import models
from profiles.models import UserProfile
from products.models import Product


class Wishlist(models.Model):
    """
    A Wishlist model for users to keep track of their favourite products.
    """
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name='user_wishlist',
        default=None
    )
    product = models.ForeignKey(
        Product,
        null=False,
        blank=False,
        related_name='wishlists',
        on_delete=models.CASCADE,
        default=None
    )

    def __str__(self):
        return self.product.name
