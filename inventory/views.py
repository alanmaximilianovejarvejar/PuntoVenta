from django.contrib import messages
from django.shortcuts import redirect, render

from inventory.forms import InventoryAdjustmentForm
from inventory.repositories.inventory_repository import InventoryRepository
from inventory.services.inventory_service import InventoryService
from products.repositories.product_repository import ProductRepository
from users.decorators import admin_required


@admin_required
def inventory_overview(request):
    context = {
        "low_stock_products": ProductRepository.low_stock(),
        "recent_movements": InventoryRepository.recent(),
    }
    return render(request, "inventory/overview.html", context)


@admin_required
def inventory_adjustment(request):
    form = InventoryAdjustmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            InventoryService.adjust_stock(
                product=form.cleaned_data["product"],
                adjustment_type=form.cleaned_data["adjustment_type"],
                quantity=form.cleaned_data["quantity"],
                reason=form.cleaned_data["reason"],
                user=request.user,
            )
            messages.success(request, "Inventario ajustado correctamente.")
            return redirect("inventory_overview")
        except ValueError as exc:
            form.add_error("quantity", str(exc))
    return render(request, "inventory/adjustment_form.html", {"form": form})

