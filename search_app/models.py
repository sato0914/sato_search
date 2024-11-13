from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Category Name"))

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Product Name"))
    description = models.TextField(verbose_name=_("Description"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Price"))
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_("Category"))
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name=_("Product Image"))

    def __str__(self):
        return self.name

    def clean(self):
        if self.price < 0:
            raise ValidationError(_('Price must be zero or greater.'))

    class Meta:
        ordering = ['name']
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    query = models.CharField(max_length=255, verbose_name=_("Search Query"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))

    def __str__(self):
        return f"{self.user.username}: {self.query} at {self.timestamp}"

    class Meta:
        verbose_name = _("Search History")
        verbose_name_plural = _("Search Histories")
