from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from core.services.sync_service import export_database_json, export_sales_csv_response, import_database_json
from inventory.repositories.inventory_repository import InventoryRepository
from products.repositories.product_repository import ProductRepository
from sales.models import Sale, SaleItem
from users.decorators import admin_required


def health(request: HttpRequest) -> JsonResponse:
    response = JsonResponse({"ok": True, "app": "cauloti-pos"})
    response["Access-Control-Allow-Origin"] = "*"
    return response


def _decimal(value: Decimal | None) -> Decimal:
    return value or Decimal("0.00")


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    now = timezone.localtime()
    today = now.date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    completed = Sale.objects.filter(status=Sale.Status.COMPLETED)
    daily_sales = completed.filter(created_at__date=today)
    weekly_sales = completed.filter(created_at__date__gte=week_start)
    monthly_sales = completed.filter(created_at__date__gte=month_start)

    top_products = (
        SaleItem.objects.filter(sale__status=Sale.Status.COMPLETED)
        .values("product_name")
        .annotate(quantity=Sum("quantity"), total=Sum("total"))
        .order_by("-quantity")[:8]
    )

    last_7_days = []
    for index in range(6, -1, -1):
        date = today - timedelta(days=index)
        total = _decimal(completed.filter(created_at__date=date).aggregate(total=Sum("total"))["total"])
        last_7_days.append({"label": date.strftime("%d/%m"), "total": float(total)})

    context = {
        "daily_total": _decimal(daily_sales.aggregate(total=Sum("total"))["total"]),
        "daily_count": daily_sales.count(),
        "weekly_total": _decimal(weekly_sales.aggregate(total=Sum("total"))["total"]),
        "monthly_total": _decimal(monthly_sales.aggregate(total=Sum("total"))["total"]),
        "top_products": top_products,
        "low_stock_count": ProductRepository.low_stock().count(),
        "active_products_count": ProductRepository.active().count(),
        "inventory_adjustments_count": InventoryRepository.manual_adjustments().count(),
        "chart_days_json": json.dumps(last_7_days),
    }
    return render(request, "core/dashboard.html", context)


@login_required
def sync_center(request: HttpRequest) -> HttpResponse:
    exports = {
        "products": ProductRepository.active().count(),
        "sales": Sale.objects.count(),
        "items": SaleItem.objects.count(),
    }
    return render(request, "core/sync.html", {"exports": exports})


@login_required
@admin_required
def export_json(request: HttpRequest) -> JsonResponse:
    payload = export_database_json()
    response = JsonResponse(payload, json_dumps_params={"indent": 2, "ensure_ascii": False})
    response["Content-Disposition"] = 'attachment; filename="cauloti-export.json"'
    return response


@login_required
@admin_required
def export_sales_csv(request: HttpRequest) -> HttpResponse:
    return export_sales_csv_response()


@login_required
@admin_required
@require_http_methods(["GET", "POST"])
def import_json(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        upload = request.FILES.get("file")
        if not upload:
            messages.error(request, "Selecciona un archivo JSON para importar.")
            return redirect("import_json")
        try:
            payload = json.loads(upload.read().decode("utf-8"))
            summary = import_database_json(payload, request.user)
            messages.success(request, f"Importacion completada: {summary}")
            return redirect("sync_center")
        except (ValueError, KeyError, TypeError) as exc:
            messages.error(request, f"No se pudo importar el archivo: {exc}")
    return render(request, "core/import.html")
