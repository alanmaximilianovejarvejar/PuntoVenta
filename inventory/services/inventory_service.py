from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction

from inventory.models import InventoryMovement
from products.models import Product


class InventoryService:
    @staticmethod
    @transaction.atomic
    def adjust_stock(
        *,
        product: Product,
        adjustment_type: str,
        quantity: Decimal,
        reason: str,
        user: User,
    ) -> InventoryMovement:
        product = Product.objects.select_for_update().get(pk=product.pk)
        if adjustment_type == "set":
            delta = quantity - product.stock_current
            product.stock_current = quantity
        else:
            delta = quantity
            product.stock_current += delta
        if product.stock_current < 0:
            raise ValueError("El ajuste dejaria el inventario en negativo.")
        product.full_clean()
        product.save(update_fields=["stock_current", "updated_at"])
        return InventoryMovement.objects.create(
            product=product,
            movement_type=InventoryMovement.Type.MANUAL,
            quantity_delta=delta,
            stock_after=product.stock_current,
            reason=reason,
            created_by=user,
        )

