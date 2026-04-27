from inventory.models import InventoryMovement


class InventoryRepository:
    @staticmethod
    def recent(limit: int = 50):
        return InventoryMovement.objects.select_related("product", "created_by", "sale").order_by("-created_at")[:limit]

    @staticmethod
    def manual_adjustments():
        return InventoryMovement.objects.filter(movement_type=InventoryMovement.Type.MANUAL)

