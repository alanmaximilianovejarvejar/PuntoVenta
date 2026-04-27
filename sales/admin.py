from django.contrib import admin

from sales.models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ("product_name", "barcode", "quantity", "unit_price", "tax_amount", "total")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("folio", "cashier", "status", "payment_method", "total", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("folio", "cashier__username")
    inlines = [SaleItemInline]

