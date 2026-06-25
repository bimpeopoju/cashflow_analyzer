from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from finance.models import CashEntry, InventoryItem, Sale, SaleLine, StockMovement


@transaction.atomic
def create_sale(*, business, payload, user=None):
    inventory_item_id = payload.pop('inventory_item_id', None)
    quantity = payload['quantity']
    amount = payload['amount']
    unit_price = (amount / quantity).quantize(Decimal('0.01')) if quantity else amount
    inventory_item = None
    unit_cost = Decimal('0.00')

    if inventory_item_id:
        inventory_item = (
            InventoryItem.objects
            .select_for_update()
            .filter(business=business, pk=inventory_item_id)
            .first()
        )
        if inventory_item is None:
            raise ValueError('Inventory item not found.')
        if inventory_item.quantity < quantity:
            raise ValueError('Not enough stock available.')
        unit_cost = inventory_item.unit_cost

    sale = Sale.objects.create(business=business, created_by=user, **payload)
    line = SaleLine.objects.create(
        sale=sale,
        inventory_item=inventory_item,
        item_name=sale.item_name,
        quantity=quantity,
        unit_price=unit_price,
        unit_cost=unit_cost,
        discount_amount=Decimal('0.00'),
        line_total=amount,
    )

    if inventory_item is not None:
        inventory_item.quantity -= quantity
        inventory_item.save(update_fields=['quantity', 'updated_at'])
        StockMovement.objects.create(
            business=business,
            inventory_item=inventory_item,
            movement_type=StockMovement.MOVEMENT_SALE,
            quantity_change=-quantity,
            unit_cost=unit_cost,
            reference_type='sale_line',
            reference_id=line.id,
            note=f'Sale #{sale.id}',
        )

    if sale.amount_paid > 0:
        CashEntry.objects.create(
            business=business,
            entry_type=CashEntry.ENTRY_SALE_PAYMENT,
            direction=CashEntry.DIRECTION_INFLOW,
            amount=sale.amount_paid,
            occurred_at=sale.sold_at,
            reference_type='sale',
            reference_id=sale.id,
            note=sale.note,
        )

    return sale


@transaction.atomic
def void_sale(*, business, pk, user=None, reason=''):
    sale = (
        Sale.objects
        .select_for_update()
        .filter(business=business, pk=pk, status=Sale.STATUS_COMPLETED)
        .first()
    )
    if sale is None:
        return False

    sale.status = Sale.STATUS_VOIDED
    sale.voided_at = timezone.now()
    sale.voided_by = user
    sale.void_reason = reason
    sale.save(update_fields=['status', 'voided_at', 'voided_by', 'void_reason'])

    for line in sale.lines.select_related('inventory_item'):
        if line.inventory_item_id:
            item = InventoryItem.objects.select_for_update().get(pk=line.inventory_item_id)
            item.quantity += line.quantity
            item.save(update_fields=['quantity', 'updated_at'])
            StockMovement.objects.create(
                business=business,
                inventory_item=item,
                movement_type=StockMovement.MOVEMENT_RETURN,
                quantity_change=line.quantity,
                unit_cost=line.unit_cost,
                reference_type='sale_void',
                reference_id=sale.id,
                note=reason or f'Voided sale #{sale.id}',
            )

    if sale.amount_paid > 0:
        CashEntry.objects.create(
            business=business,
            entry_type=CashEntry.ENTRY_SALE_PAYMENT,
            direction=CashEntry.DIRECTION_OUTFLOW,
            amount=sale.amount_paid,
            occurred_at=timezone.now(),
            reference_type='sale_void',
            reference_id=sale.id,
            note=reason or f'Voided sale #{sale.id}',
        )
    return True
