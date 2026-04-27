from __future__ import annotations

import csv
from decimal import Decimal
from io import StringIO
from typing import Any

from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone

from inventory.models import InventoryMovement
from products.models import Category, Product
from sales.models import Sale, SaleItem


def _money(value: Decimal | None) -> str:
    return str(value or Decimal("0.00"))


def export_database_json() -> dict[str, Any]:
    return {
        "schema": "cauloti-pos-v1",
        "exported_at": timezone.now().isoformat(),
        "categories": [
            {
                "name": category.name,
                "slug": category.slug,
                "description": category.description,
                "is_active": category.is_active,
            }
            for category in Category.objects.order_by("name")
        ],
        "products": [
            {
                "name": product.name,
                "sku": product.sku,
                "barcode": product.barcode,
                "category": product.category.slug if product.category else None,
                "description": product.description,
                "sale_price": _money(product.sale_price),
                "cost": _money(product.cost),
                "stock_current": _money(product.stock_current),
                "min_stock": _money(product.min_stock),
                "tax_rate": str(product.tax_rate),
                "is_active": product.is_active,
            }
            for product in Product.objects.select_related("category").order_by("name")
        ],
        "sales": [
            {
                "folio": sale.folio,
                "cashier": sale.cashier.username if sale.cashier else "",
                "status": sale.status,
                "payment_method": sale.payment_method,
                "subtotal": _money(sale.subtotal),
                "tax_total": _money(sale.tax_total),
                "total": _money(sale.total),
                "amount_received": _money(sale.amount_received),
                "change_given": _money(sale.change_given),
                "created_at": sale.created_at.isoformat(),
                "items": [
                    {
                        "product_name": item.product_name,
                        "barcode": item.barcode,
                        "quantity": _money(item.quantity),
                        "unit_price": _money(item.unit_price),
                        "tax_rate": str(item.tax_rate),
                        "subtotal": _money(item.subtotal),
                        "tax_amount": _money(item.tax_amount),
                        "total": _money(item.total),
                    }
                    for item in sale.items.all()
                ],
            }
            for sale in Sale.objects.prefetch_related("items").select_related("cashier").order_by("-created_at")
        ],
    }


def export_sales_csv_response() -> HttpResponse:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "folio",
            "fecha",
            "cajero",
            "estado",
            "metodo_pago",
            "subtotal",
            "impuestos",
            "total",
        ]
    )
    for sale in Sale.objects.select_related("cashier").order_by("-created_at"):
        writer.writerow(
            [
                sale.folio,
                timezone.localtime(sale.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                sale.cashier.username if sale.cashier else "",
                sale.status,
                sale.payment_method,
                _money(sale.subtotal),
                _money(sale.tax_total),
                _money(sale.total),
            ]
        )
    response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="cauloti-ventas.csv"'
    return response


@transaction.atomic
def import_database_json(payload: dict[str, Any], user: User) -> str:
    if payload.get("schema") != "cauloti-pos-v1":
        raise ValueError("schema no soportado")

    categories_count = 0
    products_count = 0

    category_by_slug = {}
    for row in payload.get("categories", []):
        category, _created = Category.objects.update_or_create(
            slug=row["slug"],
            defaults={
                "name": row["name"],
                "description": row.get("description", ""),
                "is_active": bool(row.get("is_active", True)),
            },
        )
        category_by_slug[category.slug] = category
        categories_count += 1

    for row in payload.get("products", []):
        category = category_by_slug.get(row.get("category"))
        product, _created = Product.objects.update_or_create(
            barcode=row["barcode"],
            defaults={
                "name": row["name"],
                "sku": row.get("sku", ""),
                "category": category,
                "description": row.get("description", ""),
                "sale_price": Decimal(row.get("sale_price", "0")),
                "cost": Decimal(row.get("cost", "0")),
                "stock_current": Decimal(row.get("stock_current", "0")),
                "min_stock": Decimal(row.get("min_stock", "0")),
                "tax_rate": Decimal(row.get("tax_rate", "0.16")),
                "is_active": bool(row.get("is_active", True)),
            },
        )
        InventoryMovement.objects.create(
            product=product,
            movement_type=InventoryMovement.Type.IMPORT,
            quantity_delta=Decimal("0"),
            stock_after=product.stock_current,
            reason="Importacion JSON",
            created_by=user,
        )
        products_count += 1

    return f"{categories_count} categorias, {products_count} productos"

