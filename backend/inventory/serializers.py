from decimal import Decimal, InvalidOperation

from finance.services import money


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


def validate_inventory_payload(data):
    return {
        'name': text_from_payload(data, 'name', 'Item name'),
        'quantity': int_from_payload(data, 'quantity', 0),
        'unit': text_from_payload(data, 'unit', 'Unit', required=False) or 'pcs',
        'reorder_level': int_from_payload(data, 'reorderLevel', 5),
        'unit_cost': decimal_from_payload(data, 'unitCost'),
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
        'status': item.status,
    }


def validate_void_payload(data):
    return {
        'reason': text_from_payload(data, 'reason', 'Reason', required=False),
    }
