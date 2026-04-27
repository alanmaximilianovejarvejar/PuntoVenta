from __future__ import annotations

from django.db import models
from django.db.models import Q, QuerySet

from products.models import Product


class ProductRepository:
    @staticmethod
    def active() -> QuerySet[Product]:
        return Product.objects.select_related("category").filter(is_active=True)

    @staticmethod
    def low_stock() -> QuerySet[Product]:
        return Product.objects.select_related("category").filter(is_active=True, stock_current__lte=models.F("min_stock"))

    @staticmethod
    def search(term: str) -> QuerySet[Product]:
        queryset = ProductRepository.active()
        if term:
            queryset = queryset.filter(
                Q(name__icontains=term)
                | Q(barcode__icontains=term)
                | Q(sku__icontains=term)
                | Q(category__name__icontains=term)
            )
        return queryset.order_by("name")

    @staticmethod
    def by_barcode(barcode: str) -> Product | None:
        return ProductRepository.active().filter(barcode=barcode).first()
