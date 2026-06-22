from .models import Expense, InventoryItem, Sale
from .services import active_memberships_for_user, ensure_default_business


def list_user_businesses(user):
    return active_memberships_for_user(user)


def default_business_for_user(user):
    return ensure_default_business(user)


def sales_for_business(business):
    return Sale.objects.filter(business=business)


def expenses_for_business(business):
    return Expense.objects.filter(business=business)


def inventory_for_business(business):
    return InventoryItem.objects.filter(business=business)


def sale_for_business(*, business, pk):
    return Sale.objects.filter(business=business, pk=pk).first()


def expense_for_business(*, business, pk):
    return Expense.objects.filter(business=business, pk=pk).first()


def inventory_item_for_business(*, business, pk):
    return InventoryItem.objects.filter(business=business, pk=pk).first()
