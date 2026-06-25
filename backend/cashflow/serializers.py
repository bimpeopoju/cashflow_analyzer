from decimal import Decimal, InvalidOperation

from businesses.services import money
from cashflow.models import CashEntry


def decimal_from_payload(data, field_name):
    raw_value = data.get(field_name)
    if raw_value in (None, ''):
        raise ValueError(f'{field_name} is required.')
    try:
        value = Decimal(str(raw_value))
    except (InvalidOperation, TypeError):
        raise ValueError(f'{field_name} must be a valid amount.') from None
    if value <= 0:
        raise ValueError(f'{field_name} must be greater than zero.')
    return value


def validate_cash_entry_payload(data):
    entry_type = str(data.get('entryType', '')).strip()
    allowed_types = {
        CashEntry.ENTRY_OWNER_DEPOSIT,
        CashEntry.ENTRY_OWNER_WITHDRAWAL,
    }
    if entry_type not in allowed_types:
        raise ValueError('entryType must be owner_deposit or owner_withdrawal.')

    amount = decimal_from_payload(data, 'amount')
    note = str(data.get('note', '')).strip()

    direction = CashEntry.DIRECTION_INFLOW if entry_type == CashEntry.ENTRY_OWNER_DEPOSIT else CashEntry.DIRECTION_OUTFLOW

    return {
        'entry_type': entry_type,
        'direction': direction,
        'amount': amount,
        'note': note,
    }


def cash_entry_payload(entry):
    return {
        'id': entry.id,
        'entryType': entry.entry_type,
        'direction': entry.direction,
        'amount': money(entry.amount),
        'note': entry.note,
        'createdAt': entry.occurred_at.isoformat(),
    }
