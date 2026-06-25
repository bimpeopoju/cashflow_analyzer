from inventory.models import InventoryItem, StockMovement


def inventory_for_business(business):
    return InventoryItem.objects.filter(business=business, status=InventoryItem.STATUS_ACTIVE)


def stock_movements_for_business(business):
    return StockMovement.objects.filter(business=business).select_related('inventory_item')


def inventory_item_for_business(*, business, pk):
    return InventoryItem.objects.filter(business=business, pk=pk).first()
