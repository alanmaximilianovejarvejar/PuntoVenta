from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name = models.CharField(max_length=180)
    sku = models.CharField(max_length=80, blank=True)
    barcode = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    stock_current = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    min_stock = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    tax_rate = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal("0.1600"))
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["barcode"]),
            models.Index(fields=["is_active"]),
        ]

    def clean(self) -> None:
        errors = {}
        if self.sale_price < 0:
            errors["sale_price"] = "El precio de venta no puede ser negativo."
        if self.cost < 0:
            errors["cost"] = "El costo no puede ser negativo."
        if self.stock_current < 0:
            errors["stock_current"] = "El stock no puede ser negativo."
        if self.min_stock < 0:
            errors["min_stock"] = "El stock minimo no puede ser negativo."
        if self.tax_rate < 0:
            errors["tax_rate"] = "El impuesto no puede ser negativo."
        if self.cost and self.sale_price and self.sale_price < self.cost:
            errors["sale_price"] = "El precio de venta debe ser mayor o igual al costo."
        if errors:
            raise ValidationError(errors)

    @property
    def is_low_stock(self) -> bool:
        return self.stock_current <= self.min_stock

    def get_absolute_url(self) -> str:
        return reverse("product_detail", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        return self.name

