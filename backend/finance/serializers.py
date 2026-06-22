from decimal import Decimal, InvalidOperation

from .services import money


def decimal_from_payload(data, field):
    try:
        value = Decimal(str(data.get(field, '0'))).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError):
        raise ValueError(f'{field} must be a valid amount.')
    if value < 0:
        raise ValueError(f'{field} cannot be negative.')
    return value


def int_from_payload(data, field, default=0):
    try:
        value = int(data.get(field, default))
    except (TypeError, ValueError):
        raise ValueError(f'{field} must be a whole number.')
    if value < 0:
        raise ValueError(f'{field} cannot be negative.')
    return value


def text_from_payload(data, field, label, required=True):
    value = str(data.get(field, '')).strip()
    if required and not value:
        raise ValueError(f'{label} is required.')
    return value


def validate_business_payload(data):
    return {
        'name': text_from_payload(data, 'name', 'Business name'),
        'stall_name': text_from_payload(data, 'stallName', 'Stall name', required=False) or 'Market stall',
        'initial_capital': decimal_from_payload(data, 'initialCapital'),
    }


def validate_sale_payload(data):
    amount = decimal_from_payload(data, 'amount')
    amount_paid = decimal_from_payload(data, 'amountPaid') if 'amountPaid' in data else amount
    if amount_paid > amount:
        raise ValueError('amountPaid cannot exceed amount.')
    if amount_paid == 0:
        payment_status = 'unpaid'
    elif amount_paid < amount:
        payment_status = 'partial'
    else:
        payment_status = 'paid'
    return {
        'inventory_item_id': int_from_payload(data, 'inventoryItemId', 0) or None,
        'item_name': text_from_payload(data, 'itemName', 'Item name'),
        'amount': amount,
        'amount_paid': amount_paid,
        'payment_status': payment_status,
        'quantity': int_from_payload(data, 'quantity', 1),
        'note': text_from_payload(data, 'note', 'Note', required=False),
    }


def validate_expense_payload(data):
    payment_status = str(data.get('paymentStatus', 'paid')).strip() or 'paid'
    if payment_status not in {'paid', 'unpaid'}:
        raise ValueError('paymentStatus must be paid or unpaid.')
    return {
        'category': text_from_payload(data, 'category', 'Category'),
        'amount': decimal_from_payload(data, 'amount'),
        'payment_status': payment_status,
        'note': text_from_payload(data, 'note', 'Note', required=False),
    }


def validate_inventory_payload(data):
    return {
        'name': text_from_payload(data, 'name', 'Item name'),
        'quantity': int_from_payload(data, 'quantity', 0),
        'unit': text_from_payload(data, 'unit', 'Unit', required=False) or 'pcs',
        'reorder_level': int_from_payload(data, 'reorderLevel', 5),
        'unit_cost': decimal_from_payload(data, 'unitCost'),
    }


def sale_payload(sale):
    first_line = sale.lines.first()
    return {
        'id': sale.id,
        'itemName': sale.item_name,
        'inventoryItemId': first_line.inventory_item_id if first_line else None,
        'amount': money(sale.amount),
        'amountPaid': money(sale.amount_paid),
        'paymentStatus': sale.payment_status,
        'quantity': sale.quantity,
        'note': sale.note,
        'createdAt': sale.sold_at.isoformat(),
    }


def expense_payload(expense):
    return {
        'id': expense.id,
        'category': expense.category,
        'amount': money(expense.amount),
        'paymentStatus': expense.payment_status,
        'note': expense.note,
        'createdAt': expense.spent_at.isoformat(),
    }


def inventory_payload(item):
    return {
        'id': item.id,
        'name': item.name,
        'quantity': item.quantity,
        'unit': item.unit,
        'reorderLevel': item.reorder_level,
        'unitCost': money(item.unit_cost),
        'stockValue': money(item.unit_cost * item.quantity),
    }
