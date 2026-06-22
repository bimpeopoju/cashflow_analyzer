from .models import CashEntry, Expense, InventoryItem, Sale, SaleLine, StockMovement
from .services import active_memberships_for_user, ensure_default_business


def list_user_businesses(user):
    return active_memberships_for_user(user)


def default_business_for_user(user):
    return ensure_default_business(user)


def sales_for_business(business):
    return Sale.objects.filter(business=business, status=Sale.STATUS_COMPLETED)


def expenses_for_business(business):
    return Expense.objects.filter(business=business, status=Expense.STATUS_APPROVED)


def inventory_for_business(business):
    return InventoryItem.objects.filter(business=business, status=InventoryItem.STATUS_ACTIVE)


def sale_lines_for_business(business):
    return SaleLine.objects.filter(sale__business=business, sale__status=Sale.STATUS_COMPLETED).select_related('sale', 'inventory_item')


def stock_movements_for_business(business):
    return StockMovement.objects.filter(business=business).select_related('inventory_item')


def cash_entries_for_business(business):
    return CashEntry.objects.filter(business=business)


def sale_for_business(*, business, pk):
    return Sale.objects.filter(business=business, pk=pk).first()


def expense_for_business(*, business, pk):
    return Expense.objects.filter(business=business, pk=pk).first()


def inventory_item_for_business(*, business, pk):
    return InventoryItem.objects.filter(business=business, pk=pk).first()
