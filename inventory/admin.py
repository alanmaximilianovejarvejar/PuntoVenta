from django.contrib import admin

from inventory.models import InventoryMovement


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ("product", "movement_type", "quantity_delta", "stock_after", "created_by", "created_at")
    list_filter = ("movement_type", "created_at")
    search_fields = ("product__name", "product__barcode", "reason")

