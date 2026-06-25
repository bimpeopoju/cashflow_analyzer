from decimal import Decimal, InvalidOperation

from businesses.services import business_payload


def decimal_from_payload(data, field):
    try:
        value = Decimal(str(data.get(field, '0'))).quantize(Decimal('0.01'))
    except (InvalidOperation, TypeError):
        raise ValueError(f'{field} must be a valid amount.')
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
