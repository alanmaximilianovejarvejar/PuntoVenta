from __future__ import annotations

from django.conf import settings
from django.db import models


class InventoryMovement(models.Model):
    class Type(models.TextChoices):
        SALE = "sale", "Venta"
        MANUAL = "manual", "Ajuste manual"
        CANCEL = "cancel", "Cancelacion"
        IMPORT = "import", "Importacion"

    product = models.ForeignKey("products.Product", on_delete=models.PROTECT, related_name="inventory_movements")
    sale = models.ForeignKey("sales.Sale", on_delete=models.SET_NULL, null=True, blank=True, related_name="inventory_movements")
    movement_type = models.CharField(max_length=20, choices=Type.choices)
    quantity_delta = models.DecimalField(max_digits=12, decimal_places=2)
    stock_after = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=240, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "created_at"]),
            models.Index(fields=["movement_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.product} {self.quantity_delta}"

