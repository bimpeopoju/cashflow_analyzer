from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import (
    Business,
    BusinessMembership,
    BusinessProfile,
    CashEntry,
    Expense,
    InventoryItem,
    Sale,
    SaleLine,
    StockMovement,
)


def money(value):
    return str((value or Decimal('0.00')).quantize(Decimal('0.01')))


def business_payload(business, role=None):
    return {
        'id': business.id,
        'name': business.name,
        'stallName': business.stall_name,
        'initialCapital': money(business.initial_capital),
        'role': role,
    }


@transaction.atomic
def create_business_for_user(
    *,
    user,
    name,
    stall_name='Market stall',
    initial_capital=Decimal('0.00'),
):
    business = Business.objects.create(
        owner=user,
        name=name,
        stall_name=stall_name,
        initial_capital=initial_capital,
    )
    BusinessMembership.objects.create(
        business=business,
        user=user,
        role=BusinessMembership.ROLE_OWNER,
        status=BusinessMembership.STATUS_ACTIVE,
    )
    BusinessProfile.objects.get_or_create(
        user=user,
        defaults={
            'business_name': name,
            'stall_name': stall_name,
            'initial_capital': initial_capital,
        },
    )
    return business


def active_memberships_for_user(user):
    ensure_default_business(user)
    return (
        BusinessMembership.objects
        .filter(user=user, status=BusinessMembership.STATUS_ACTIVE)
        .select_related('business')
        .order_by('business__name', 'id')
    )


def ensure_default_business(user):
    membership = (
        BusinessMembership.objects
        .filter(user=user, status=BusinessMembership.STATUS_ACTIVE)
        .select_related('business')
        .order_by('business__name', 'id')
        .first()
    )
    if membership:
        return membership.business

    profile, _ = BusinessProfile.objects.get_or_create(
        user=user,
        defaults={
            'business_name': f"{user.first_name or 'MarketFlow'} Business",
            'stall_name': 'Market stall',
        },
    )
    return create_business_for_user(
        user=user,
        name=profile.business_name,
        stall_name=profile.stall_name or 'Market stall',
        initial_capital=profile.initial_capital,
    )


def get_business_for_user(user, business_id=None):
    if business_id is None:
        return ensure_default_business(user)

    membership = (
        BusinessMembership.objects
        .filter(
            user=user,
            business_id=business_id,
            status=BusinessMembership.STATUS_ACTIVE,
        )
        .select_related('business')
        .first()
    )
    return membership.business if membership else None


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


def delete_sale(*, business, pk):
    return int(void_sale(business=business, pk=pk))


def create_expense(*, business, payload, user=None):
    expense = Expense.objects.create(business=business, created_by=user, **payload)
    if expense.payment_status == Expense.PAYMENT_PAID and expense.amount > 0:
        CashEntry.objects.create(
            business=business,
            entry_type=CashEntry.ENTRY_EXPENSE_PAYMENT,
            direction=CashEntry.DIRECTION_OUTFLOW,
            amount=expense.amount,
            occurred_at=expense.spent_at,
            reference_type='expense',
            reference_id=expense.id,
            note=expense.note,
        )
    return expense


@transaction.atomic
def void_expense(*, business, pk, user=None, reason=''):
    expense = (
        Expense.objects
        .select_for_update()
        .filter(business=business, pk=pk, status=Expense.STATUS_APPROVED)
        .first()
    )
    if expense is None:
        return False

    expense.status = Expense.STATUS_VOIDED
    expense.voided_at = timezone.now()
    expense.voided_by = user
    expense.void_reason = reason
    expense.save(update_fields=['status', 'voided_at', 'voided_by', 'void_reason'])

    if expense.payment_status == Expense.PAYMENT_PAID and expense.amount > 0:
        CashEntry.objects.create(
            business=business,
            entry_type=CashEntry.ENTRY_EXPENSE_PAYMENT,
            direction=CashEntry.DIRECTION_INFLOW,
            amount=expense.amount,
            occurred_at=timezone.now(),
            reference_type='expense_void',
            reference_id=expense.id,
            note=reason or f'Voided expense #{expense.id}',
        )
    return True


def delete_expense(*, business, pk):
    return int(void_expense(business=business, pk=pk))


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


def delete_inventory_item(*, business, pk):
    return int(void_inventory_item(business=business, pk=pk))
