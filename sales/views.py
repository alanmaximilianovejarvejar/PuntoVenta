from __future__ import annotations

import json
from decimal import Decimal
from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from products.repositories.product_repository import ProductRepository
from products.models import Product
from sales.forms import SaleFilterForm, VoidSaleForm
from sales.models import Sale
from sales.repositories.sale_repository import SaleRepository
from sales.services.sale_service import SaleService
from users.decorators import admin_required, cashier_or_admin_required


@cashier_or_admin_required
def pos(request: HttpRequest) -> HttpResponse:
    return render(request, "sales/pos.html")


@login_required
@require_GET
def search_products(request: HttpRequest) -> JsonResponse:
    term = request.GET.get("q", "").strip()
    products = ProductRepository.search(term)[:15]
    results = []
    for product in products:
        results.append(
            {
                "id": product.id,
                "name": product.name,
                "barcode": product.barcode,
                "category": product.category.name if product.category else "",
                "sale_price": str(product.sale_price),
                "tax_rate": str(product.tax_rate),
                "stock_current": str(product.stock_current),
                "image_url": product.image.url if product.image else "",
            }
        )
    return JsonResponse({"results": results})


@cashier_or_admin_required
@require_POST
def checkout(request: HttpRequest) -> JsonResponse:
    try:
        payload = json.loads(request.body.decode("utf-8"))
        sale = SaleService.create_sale(
            cashier=request.user,
            items=payload.get("items", []),
            payment_method=payload.get("payment_method", ""),
            amount_received=Decimal(str(payload.get("amount_received", "0"))),
        )
        return JsonResponse(
            {
                "ok": True,
                "sale_id": sale.id,
                "folio": sale.folio,
                "ticket_url": reverse("sale_ticket", kwargs={"pk": sale.pk}),
                "pdf_url": reverse("sale_ticket_pdf", kwargs={"pk": sale.pk}),
            }
        )
    except (json.JSONDecodeError, ValueError, Product.DoesNotExist) as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@login_required
def sale_history(request: HttpRequest) -> HttpResponse:
    form = SaleFilterForm(request.GET or None)
    queryset = SaleRepository.search()
    if form.is_valid():
        queryset = SaleRepository.search(
            start=form.cleaned_data.get("start"),
            end=form.cleaned_data.get("end"),
            folio=form.cleaned_data.get("folio", ""),
        )
    paginator = Paginator(queryset, 25)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "sales/history.html", {"form": form, "page_obj": page_obj})


@login_required
def sale_detail(request: HttpRequest, pk: int) -> HttpResponse:
    sale = get_object_or_404(Sale.objects.select_related("cashier").prefetch_related("items"), pk=pk)
    void_form = VoidSaleForm()
    return render(request, "sales/detail.html", {"sale": sale, "void_form": void_form})


@login_required
def sale_ticket(request: HttpRequest, pk: int) -> HttpResponse:
    sale = get_object_or_404(Sale.objects.select_related("cashier").prefetch_related("items"), pk=pk)
    return render(request, "sales/ticket.html", {"sale": sale})


@login_required
def sale_ticket_pdf(request: HttpRequest, pk: int) -> HttpResponse:
    sale = get_object_or_404(Sale.objects.select_related("cashier").prefetch_related("items"), pk=pk)
    try:
        from reportlab.lib.units import mm
        from reportlab.pdfgen import canvas
    except ImportError:
        return HttpResponse("Instala reportlab para generar PDF.", status=500)

    buffer = BytesIO()
    width = 80 * mm
    height = max(120 * mm, (80 + sale.items.count() * 8) * mm)
    pdf = canvas.Canvas(buffer, pagesize=(width, height))
    y = height - 10 * mm
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawCentredString(width / 2, y, "Punto de Venta Cauloti")
    y -= 6 * mm
    pdf.setFont("Helvetica", 8)
    pdf.drawCentredString(width / 2, y, sale.folio)
    y -= 8 * mm
    for item in sale.items.all():
        pdf.drawString(5 * mm, y, f"{item.quantity} x {item.product_name[:24]}")
        y -= 4 * mm
        pdf.drawRightString(width - 5 * mm, y, f"${item.total}")
        y -= 5 * mm
    y -= 2 * mm
    pdf.line(5 * mm, y, width - 5 * mm, y)
    y -= 6 * mm
    pdf.drawString(5 * mm, y, "Subtotal")
    pdf.drawRightString(width - 5 * mm, y, f"${sale.subtotal}")
    y -= 5 * mm
    pdf.drawString(5 * mm, y, "Impuestos")
    pdf.drawRightString(width - 5 * mm, y, f"${sale.tax_total}")
    y -= 6 * mm
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(5 * mm, y, "Total")
    pdf.drawRightString(width - 5 * mm, y, f"${sale.total}")
    pdf.showPage()
    pdf.save()
    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{sale.folio}.pdf"'
    return response


@admin_required
@require_POST
def sale_cancel(request: HttpRequest, pk: int) -> HttpResponse:
    sale = get_object_or_404(Sale, pk=pk)
    form = VoidSaleForm(request.POST)
    if form.is_valid():
        try:
            SaleService.void_sale(sale=sale, user=request.user, reason=form.cleaned_data["reason"])
            messages.success(request, f"Venta cancelada: {sale.folio}")
        except ValueError as exc:
            messages.error(request, str(exc))
    else:
        messages.error(request, "Motivo de cancelacion invalido.")
    return redirect("sale_detail", pk=pk)
