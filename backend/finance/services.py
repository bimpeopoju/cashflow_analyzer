from decimal import Decimal

from django.db import transaction

from .models import Business, BusinessMembership, BusinessProfile
from .models import Expense, InventoryItem, Sale, SaleLine, StockMovement


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
def create_sale(*, business, payload):
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

    sale = Sale.objects.create(business=business, **payload)
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

    return sale


def delete_sale(*, business, pk):
    return Sale.objects.filter(business=business, pk=pk).delete()[0]


def create_expense(*, business, payload):
    return Expense.objects.create(business=business, **payload)


def delete_expense(*, business, pk):
    return Expense.objects.filter(business=business, pk=pk).delete()[0]


def create_inventory_item(*, business, payload):
    return InventoryItem.objects.create(business=business, **payload)


def delete_inventory_item(*, business, pk):
    return InventoryItem.objects.filter(business=business, pk=pk).delete()[0]
