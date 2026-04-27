from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from inventory.models import InventoryMovement
from products.models import Product
from sales.models import Sale, SaleItem


TWOPLACES = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


class SaleService:
    @staticmethod
    @transaction.atomic
    def create_sale(
        *,
        cashier: User,
        items: Iterable[dict],
        payment_method: str,
        amount_received: Decimal,
    ) -> Sale:
        rows = list(items)
        if not rows:
            raise ValueError("El carrito esta vacio.")
        if payment_method not in Sale.PaymentMethod.values:
            raise ValueError("Metodo de pago no valido.")

        sale = Sale.objects.create(
            cashier=cashier,
            payment_method=payment_method,
            amount_received=Decimal("0.00"),
            change_given=Decimal("0.00"),
        )

        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")
        total = Decimal("0.00")

        for row in rows:
            product_id = row.get("product_id")
            quantity = Decimal(str(row.get("quantity", "0")))
            if quantity <= 0:
                raise ValueError("Todas las cantidades deben ser mayores a cero.")

            product = Product.objects.select_for_update().get(pk=product_id, is_active=True)
            if product.stock_current < quantity:
                raise ValueError(f"Stock insuficiente para {product.name}. Disponible: {product.stock_current}.")

            line_subtotal = money(product.sale_price * quantity)
            line_tax = money(line_subtotal * product.tax_rate)
            line_total = money(line_subtotal + line_tax)

            SaleItem.objects.create(
                sale=sale,
                product=product,
                product_name=product.name,
                barcode=product.barcode,
                quantity=quantity,
                unit_price=product.sale_price,
                unit_cost=product.cost,
                tax_rate=product.tax_rate,
                subtotal=line_subtotal,
                tax_amount=line_tax,
                total=line_total,
            )

            product.stock_current = product.stock_current - quantity
            product.save(update_fields=["stock_current", "updated_at"])
            InventoryMovement.objects.create(
                product=product,
                sale=sale,
                movement_type=InventoryMovement.Type.SALE,
                quantity_delta=-quantity,
                stock_after=product.stock_current,
                reason=f"Venta {sale.folio}",
                created_by=cashier,
            )

            subtotal += line_subtotal
            tax_total += line_tax
            total += line_total

        subtotal = money(subtotal)
        tax_total = money(tax_total)
        total = money(total)

        if payment_method == Sale.PaymentMethod.CASH:
            amount_received = money(amount_received)
            if amount_received < total:
                raise ValueError("El efectivo recibido es menor al total.")
            change_given = money(amount_received - total)
        else:
            amount_received = total
            change_given = Decimal("0.00")

        sale.subtotal = subtotal
        sale.tax_total = tax_total
        sale.total = total
        sale.amount_received = amount_received
        sale.change_given = change_given
        sale.save(update_fields=["subtotal", "tax_total", "total", "amount_received", "change_given"])
        return sale

    @staticmethod
    @transaction.atomic
    def void_sale(*, sale: Sale, user: User, reason: str) -> Sale:
        sale = Sale.objects.select_for_update().prefetch_related("items").get(pk=sale.pk)
        if sale.status == Sale.Status.VOIDED:
            raise ValueError("La venta ya esta cancelada.")
        if not reason.strip():
            raise ValueError("Escribe el motivo de cancelacion.")

        for item in sale.items.select_related("product"):
            product = Product.objects.select_for_update().get(pk=item.product.pk)
            product.stock_current = product.stock_current + item.quantity
            product.save(update_fields=["stock_current", "updated_at"])
            InventoryMovement.objects.create(
                product=product,
                sale=sale,
                movement_type=InventoryMovement.Type.CANCEL,
                quantity_delta=item.quantity,
                stock_after=product.stock_current,
                reason=reason,
                created_by=user,
            )

        sale.status = Sale.Status.VOIDED
        sale.void_reason = reason
        sale.voided_at = timezone.now()
        sale.save(update_fields=["status", "void_reason", "voided_at"])
        return sale

