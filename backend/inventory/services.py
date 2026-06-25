from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from cashflow.models import CashEntry
from inventory.models import InventoryItem


@transaction.atomic
def create_inventory_item(*, business, payload, user=None):
    item = InventoryItem.objects.create(business=business, created_by=user, **payload)
    stock_value = (item.unit_cost * item.quantity).quantize(Decimal('0.01'))
    if stock_value > 0:
        CashEntry.objects.create(
            business=business,
            entry_type=CashEntry.ENTRY_INVENTORY_PURCHASE,
            direction=CashEntry.DIRECTION_OUTFLOW,
            amount=stock_value,
            occurred_at=timezone.now(),
            reference_type='inventory_item',
            reference_id=item.id,
            note=f'Initial stock for {item.name}',
        )
    return item


@transaction.atomic
def void_inventory_item(*, business, pk, user=None, reason=''):
    item = (
        InventoryItem.objects
        .select_for_update()
        .filter(business=business, pk=pk, status=InventoryItem.STATUS_ACTIVE)
        .first()
    )
    if item is None:
        return False

    item.status = InventoryItem.STATUS_VOIDED
    item.voided_at = timezone.now()
    item.voided_by = user
    item.void_reason = reason
    item.save(update_fields=['status', 'voided_at', 'voided_by', 'void_reason'])

    stock_value = (item.unit_cost * item.quantity).quantize(Decimal('0.01'))
    if stock_value > 0:
        CashEntry.objects.create(
            business=business,
            entry_type=CashEntry.ENTRY_INVENTORY_PURCHASE,
            direction=CashEntry.DIRECTION_INFLOW,
            amount=stock_value,
            occurred_at=timezone.now(),
            reference_type='inventory_item_void',
            reference_id=item.id,
            note=reason or f'Voided inventory item #{item.id}',
        )
    return True
