from django.db.models import QuerySet

from sales.models import Sale


class SaleRepository:
    @staticmethod
    def completed() -> QuerySet[Sale]:
        return Sale.objects.filter(status=Sale.Status.COMPLETED)

    @staticmethod
    def search(*, start=None, end=None, folio: str = "") -> QuerySet[Sale]:
        queryset = Sale.objects.select_related("cashier").prefetch_related("items").order_by("-created_at")
        if start:
            queryset = queryset.filter(created_at__date__gte=start)
        if end:
            queryset = queryset.filter(created_at__date__lte=end)
        if folio:
            queryset = queryset.filter(folio__icontains=folio)
        return queryset

